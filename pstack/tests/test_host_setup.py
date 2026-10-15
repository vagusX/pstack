import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

PSTACK = Path(__file__).resolve().parents[1]

class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='pstack-setup-')
        self.project = Path(self.tmp.name) / 'project'; self.project.mkdir()
        self.home = Path(self.tmp.name) / 'home'; self.home.mkdir()
        skills=self.project / '.agents/skills'; shutil.copytree(PSTACK/'skills',skills)
        (self.project/'.claude').mkdir(); (self.project/'.claude/skills').symlink_to(skills, target_is_directory=True)
        self.carrier=skills/'setup-pstack'; self.script=self.carrier/'scripts/setup.py'
        self.sha='a'*40
    def tearDown(self): self.tmp.cleanup()
    def run_setup(self, host='codex', *extra, success=True):
        import os
        result=subprocess.run(['python3',str(self.script),'--host',host,'--project',str(self.project),'--source-commit',self.sha,*extra],env={**os.environ,'HOME':str(self.home),'CODEX_HOME':str(self.home/'.codex')},text=True,capture_output=True)
        self.assertEqual(result.returncode,0 if success else 1,result.stdout+result.stderr)
        return result
    def receipt(self,host='codex'): return json.loads((self.project/f'.pstack/setup-{host}.json').read_text())
    def seal(self):
        f=self.carrier/'manifest.json'; data=json.loads(f.read_text()); data['adapter_version']+='-updated'
        for name in data['shared_files']:
            data['shared_files'][name]=hashlib.sha256((self.carrier/name).read_bytes()).hexdigest()
        f.write_text(json.dumps(data))
    def checksum(self,path): return hashlib.sha256(path.read_bytes()).hexdigest()
    def test_preview_and_idempotence(self):
        self.run_setup(); self.assertFalse((self.project/'AGENTS.md').exists())
        self.run_setup('codex','--write'); state=self.receipt()
        self.assertEqual(state['source_commit'],self.sha)
        self.assertNotEqual(state['source_commit'],state['upstream_commit'])
        files={p:p.stat().st_mtime_ns for p in [self.project/'AGENTS.md',self.project/'.codex/agents/poteto-agent.toml',self.project/'.pstack/setup-codex.json']}
        self.run_setup('codex','--write')
        self.assertEqual(files,{p:p.stat().st_mtime_ns for p in files})
        agent=tomllib.loads((self.project/'.codex/agents/poteto-agent.toml').read_text())
        self.assertIn('Read the `poteto-mode`',agent['developer_instructions'])
    def test_both_hosts_and_full_personas(self):
        self.run_setup('codex','--write'); self.run_setup('claude-code','--write')
        agent=(self.project/'.claude/agents/poteto-agent.md').read_text()
        self.assertIn('background: true',agent); self.assertNotIn('is_background',agent)
        comment=(self.project/'.claude/agents/comment-sicko.md').read_text()
        self.assertIn('Yes... Ha ha ha... Yes!',comment); self.assertIn('I never write application code.',comment)
    def test_upstream_updates_preserve_reviewed_model_and_permissions(self):
        for host,filename in [('codex','.codex/agents/poteto-agent.toml'),('claude-code','.claude/agents/poteto-agent.md')]:
            self.run_setup(host,'--write'); agent=self.project/filename
            if host=='codex': agent.write_text(agent.read_text()+'model = "user-model"\nmodel_reasoning_effort = "high"\n')
            else: agent.write_text(agent.read_text().replace('model: inherit','model: user-model\npermissionMode: default\ntools: Read, Glob, Grep'))
            self.run_setup(host,'--write',success=False)
            self.run_setup(host,'--write','--accept-merge',filename+'='+self.checksum(agent))
            persona=self.carrier/'agents/poteto-agent.md'; persona.write_text(persona.read_text()+'\nAn upstream behavior update.\n'); self.seal()
            self.run_setup(host,'--write')
            self.assertIn('An upstream behavior update.',agent.read_text()); self.assertIn('user-model',agent.read_text())
            if host=='claude-code': self.assertIn('tools: Read, Glob, Grep',agent.read_text())
    def test_local_changes_refused_even_without_upstream_change(self):
        self.run_setup('codex','--write'); agent=self.project/'.codex/agents/comment-sicko.toml'; agent.write_text(agent.read_text()+'model = "personal"\n'); before=agent.read_bytes(); receipt=self.receipt()
        self.run_setup('codex','--write',success=False); self.assertEqual(before,agent.read_bytes()); self.assertEqual(receipt,self.receipt())
    def test_same_name_without_receipt_and_exact_adoption(self):
        agent=self.project/'.codex/agents/comment-sicko.toml'; agent.parent.mkdir(parents=True); agent.write_text('name = "comment-sicko"\ndescription = "My own reviewer"\ndeveloper_instructions = "My reviewer behavior"\n')
        self.run_setup('codex','--write',success=False)
        self.run_setup('codex','--write','--accept-merge','.codex/agents/comment-sicko.toml='+'f'*64,success=False)
        self.run_setup('codex','--write','--accept-merge','.codex/agents/comment-sicko.toml='+self.checksum(agent))
        self.run_setup('codex','--write'); self.assertIn('My reviewer behavior',agent.read_text())
        persona=self.carrier/'agents/comment-sicko.md'; persona.write_text(persona.read_text()+'\nUpdated upstream.\n'); self.seal()
        self.run_setup('codex','--write',success=False); self.assertIn('My reviewer behavior',agent.read_text())
    def test_adopted_block_keeps_local_instruction_and_model_changes(self):
        instructions=self.project/'AGENTS.md'; instructions.write_text('Project-owned instructions.\n')
        self.run_setup('codex','--write'); instructions.write_text(instructions.read_text().replace('<!-- pstack:end -->','My local instruction.\npstack-role feature: inherit-parent\n<!-- pstack:end -->'))
        self.run_setup('codex','--write','--accept-merge','AGENTS.md='+self.checksum(instructions))
        instructions.write_text(instructions.read_text().replace('inherit-parent\n<!-- pstack:end -->','confirmed-model\n<!-- pstack:end -->')+'Unrelated new project prose.\n')
        self.run_setup('codex','--write'); self.assertIn('My local instruction.',instructions.read_text()); self.assertIn('confirmed-model',instructions.read_text()); self.assertIn('Unrelated new project prose.',instructions.read_text())
    def test_pack_updates_keep_user_owned_files_and_refuse_local_conflicts(self):
        self.run_setup('codex','--write','--benny'); pack=self.project/'.pstack/automations/benny'
        local=pack/'my-own-file.txt'; local.write_text('keep me')
        cfg=self.project/'.pstack/benny/configuration.yaml'; cfg.parent.mkdir(); cfg.write_text('user-owned: true')
        original=pack/'FOR_AGENTS.md'; original.write_text(original.read_text()+'\nMy pack customization.\n')
        self.run_setup('codex','--write','--benny',success=False)
        self.assertEqual(local.read_text(),'keep me'); self.assertEqual(cfg.read_text(),'user-owned: true')
        self.run_setup('codex','--write','--benny','--accept-merge','.pstack/automations/benny/FOR_AGENTS.md='+self.checksum(original))
        self.run_setup('codex','--write','--benny'); self.assertIn('My pack customization.',original.read_text())
    def test_corrupt_manifest_and_receipt_fail_closed(self):
        self.run_setup('codex','--write'); path=self.project/'.pstack/setup-codex.json'; data=self.receipt(); data['files']['AGENTS.md']['sha256']='0'*64; path.write_text(json.dumps(data)); self.run_setup('codex','--write',success=False)
        path.unlink(); manifest=self.carrier/'manifest.json'; manifest.write_text('{broken'); self.run_setup('codex','--write',success=False)
    def test_two_hosts_share_pack_ownership(self):
        self.run_setup('codex','--write','--benny')
        pack=self.project/'.pstack/automations/benny/FOR_AGENTS.md'; stamp=pack.stat().st_mtime_ns
        self.run_setup('claude-code','--write','--benny')
        self.assertEqual(stamp,pack.stat().st_mtime_ns)
        self.assertIn('.pstack/automations/benny/FOR_AGENTS.md',self.receipt('claude-code')['files'])
        source=self.carrier/'automations/benny/FOR_AGENTS.md'; source.write_text(source.read_text()+'\nUpdated shared pack instructions.\n'); self.seal()
        self.run_setup('codex','--write','--benny'); stamp=pack.stat().st_mtime_ns
        self.run_setup('claude-code','--write','--benny')
        self.assertEqual(stamp,pack.stat().st_mtime_ns)
        self.assertIn('Updated shared pack instructions.',pack.read_text())
    def test_missing_dependency_and_mixed_skill_rejected(self):
        skill=self.project/'.agents/skills/poteto-mode'; (skill/'SKILL.md').write_text('wrong version'); self.run_setup('codex','--write',success=False)
        shutil.rmtree(skill); self.run_setup('codex','--write',success=False)
    def test_global_copy_cannot_bypass_project_setup(self):
        global_skills=self.home/'.agents/skills'; shutil.copytree(self.project/'.agents/skills',global_skills)
        self.script=global_skills/'setup-pstack/scripts/setup.py'; self.run_setup('codex','--check',success=False)
    def test_unordered_marker_and_linked_destination_rejected(self):
        (self.project/'AGENTS.md').write_text('<!-- pstack:end -->\n<!-- pstack:begin -->'); self.run_setup('codex','--write',success=False)
        (self.project/'AGENTS.md').unlink(); shutil.rmtree(self.project/'.pstack'); outside=Path(self.tmp.name)/'outside'; outside.mkdir(); (self.project/'.pstack').symlink_to(outside,target_is_directory=True)
        self.run_setup('codex','--write',success=False); self.assertFalse((outside/'setup-codex.json').exists())
    def test_actual_install_commit_required_on_first_write(self):
        import os
        result=subprocess.run(['python3',str(self.script),'--host','codex','--project',str(self.project),'--write'],env={**os.environ,'HOME':str(self.home),'CODEX_HOME':str(self.home/'.codex')},text=True,capture_output=True)
        self.assertEqual(result.returncode,1); self.assertIn('actual Git commit',result.stderr)

if __name__=='__main__': unittest.main()
