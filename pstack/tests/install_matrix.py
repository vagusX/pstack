#!/usr/bin/env python3
"""Real skills@1.7.2 installs under isolated homes; optional Bun CLI/cache checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

PSTACK=Path(__file__).resolve().parents[1]

def tree(path):
    return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}

def run(command, cwd, env, success=True):
    result=subprocess.run(command,cwd=cwd,env=env,text=True,capture_output=True)
    if (result.returncode==0) != success: raise AssertionError(f'{command}:\n{result.stdout}\n{result.stderr}')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--node',required=True,type=Path); parser.add_argument('--cli',required=True,type=Path); parser.add_argument('--bun',type=Path); parser.add_argument('--output',type=Path); parser.add_argument('--upgrade-from',type=Path,help='Parent pstack tree with the retired support skill'); args=parser.parse_args()
    version=json.loads((args.cli.resolve().parents[1]/'package.json').read_text())['version']
    if version!='1.7.2': raise ValueError(f'Expected skills 1.7.2, found {version}')
    node=str(args.node.resolve()); cli=str(args.cli.resolve()); bun=str(args.bun.resolve()) if args.bun else None
    rows=[]
    with tempfile.TemporaryDirectory(prefix='pstack-install-matrix-') as temporary:
        base=Path(temporary)
        for host in ['codex','claude-code']:
            for scope in ['project','global']:
                for selection in ['full','subset']:
                    for mode in ['copy','link']:
                        name=f'{host}-{scope}-{selection}-{mode}'; case=base/name; case.mkdir(); home=case/'home'; home.mkdir(); project=case/'project'; project.mkdir(); source=case/'source'; shutil.copytree(PSTACK,source)
                        env={**os.environ,'HOME':str(home),'CODEX_HOME':str(home/'.codex'),'CLAUDE_CONFIG_DIR':str(home/'.claude'),'XDG_CONFIG_HOME':str(home/'.config'),'DISABLE_TELEMETRY':'1','DO_NOT_TRACK':'1'}
                        listed=run([node,cli,'add',str(source),'--list','--full-depth'],project,env).stdout
                        assert 'Found 54 skills' in listed,listed
                        for forbidden in ['triage-issue-reports\n','reproduce-and-fix-issues\n','setup-benny\n']: assert forbidden not in listed
                        selected=['*'] if selection=='full' else ['setup-pstack','Poteto Mode']
                        command=[node,cli,'add',str(source),'--skill',*selected,'--agent',host,'-y','--json']
                        if scope=='global': command+=['--global']
                        if mode=='copy': command+=['--copy']
                        result=run(command,project,env)
                        installed_base=home if scope=='global' else project
                        skills=installed_base/('.agents/skills' if host=='codex' else '.claude/skills')
                        carrier=skills/'setup-pstack'; assert carrier.is_dir(),result.stdout
                        installed_names={p.name for p in skills.iterdir() if p.is_dir()}
                        expected=54 if selection=='full' else 2
                        assert len(installed_names)==expected,(name,installed_names)
                        assert not {'pstack-support','setup-benny','triage-issue-reports','reproduce-and-fix-issues'} & installed_names
                        script=carrier/'scripts/setup.py'
                        # Prove installation does not depend on its source checkout.
                        shutil.rmtree(source)
                        before=tree(skills)
                        run(['python3',str(script),'--host',host,'--project',str(project),'--check'],project,env)
                        run(['python3',str(script),'--host',host,'--project',str(project),'--source-commit','a'*40,'--benny','--write'],project,env)
                        run(['python3',str(script),'--host',host,'--project',str(project),'--benny','--write'],project,env)
                        assert (project/'.pstack/automations/benny/skills/setup-benny/INSTRUCTIONS.md').is_file()
                        assert before==tree(skills),(name,'installed files changed after setup')
                        if bun and selection=='full' and scope=='project' and mode=='link':
                            tool=skills/'poteto-mode/scripts'; marker_times={}
                            for relative in ['orch/orch.ts','watch-pr/watch-pr']:
                                run([bun,str(tool/relative),'--help'],project,env)
                            cache=project/'.pstack/runtime/poteto-tools'; marker_times={str(p):p.stat().st_mtime_ns for p in cache.glob('*/.install-key')}
                            assert len(marker_times)==1
                            run([bun,str(tool/'orch/orch.ts'),'--help'],project,env)
                            assert marker_times=={str(p):p.stat().st_mtime_ns for p in cache.glob('*/.install-key')}
                            assert before==tree(skills),(name,'bootstrap wrote installed skills')
                            bad=case/'linked-project'; bad.mkdir(); (bad/'.pstack').symlink_to((skills/'poteto-mode').resolve(),target_is_directory=True)
                            failed=run([bun,str(tool/'orch/orch.ts'),'--help'],bad,env,False); assert 'linked runtime' in failed.stderr
                            inside=(skills/'poteto-mode').resolve()/'..calling-project'; inside.mkdir()
                            run([bun,str(tool/'orch/orch.ts'),'--help'],inside,env,False); inside.rmdir()
                            assert before==tree(skills)
                            updated=case/'updated-poteto-mode'; shutil.copytree(skills/'poteto-mode',updated); lock=updated/'scripts/bun.lock'; lock.write_text(lock.read_text()+'\n')
                            updated_before=tree(updated)
                            run([bun,str(updated/'scripts/orch/orch.ts'),'--help'],project,env)
                            assert len(list(cache.glob('*/.install-key')))==2
                            assert updated_before==tree(updated)
                        rows.append({'host':host,'scope':scope,'selection':selection,'mode':mode,'count':expected,'source_removed':True,'setup_readback':True,'installed_hash_unchanged':True})
                        print(f'PASS {name}',flush=True)
        # Multi-host default links share canonical published content without source links.
        case=base/'multi-host'; case.mkdir(); project=case/'project'; project.mkdir(); home=case/'home'; home.mkdir(); source=case/'source'; shutil.copytree(PSTACK,source)
        env={**os.environ,'HOME':str(home),'CODEX_HOME':str(home/'.codex'),'CLAUDE_CONFIG_DIR':str(home/'.claude'),'DISABLE_TELEMETRY':'1'}
        run([node,cli,'add',str(source),'--skill','*','--agent','codex','claude-code','-y'],project,env); shutil.rmtree(source)
        assert (project/'.claude/skills/setup-pstack').resolve()==(project/'.agents/skills/setup-pstack').resolve()
        rows.append({'host':'codex+claude-code','mode':'shared-links','count':54,'source_removed':True})
        print('PASS multi-host shared links',flush=True)
        # A workflow can read the shared carrier without running project setup.
        case=base/'minimal-how'; case.mkdir(); project=case/'project'; project.mkdir(); home=case/'home'; home.mkdir(); source=case/'source'; shutil.copytree(PSTACK,source)
        env={**os.environ,'HOME':str(home),'CODEX_HOME':str(home/'.codex'),'CLAUDE_CONFIG_DIR':str(home/'.claude'),'DISABLE_TELEMETRY':'1'}
        run([node,cli,'add',str(source),'--skill','how','setup-pstack','--agent','codex','claude-code','--copy','-y'],project,env)
        shutil.rmtree(source)
        for host,directory in [('codex','.agents/skills'),('claude-code','.claude/skills')]:
            skills=project/directory
            assert {p.name for p in skills.iterdir()}=={'how','setup-pstack'}
            before=tree(skills)
            run(['python3',str(skills/'setup-pstack/scripts/setup.py'),'--host',host,'--project',str(project),'--check','--require','how','--skill-location',str(skills/'how')],project,env)
            assert before==tree(skills)
        assert not (project/'.pstack').exists()
        assert not (project/'.codex/agents').exists() and not (project/'.claude/agents').exists()
        rows.append({'host':'codex+claude-code','case':'minimal-how-plus-setup','count':2,'project_configuration_written':False,'installed_hash_unchanged':True})
        print('PASS how + setup-pstack preflight without configuration',flush=True)
        if args.upgrade_from:
            case=base/'carrier-upgrade'; case.mkdir(); project=case/'project'; project.mkdir(); home=case/'home'; home.mkdir()
            old_source=case/'old-source'; shutil.copytree(args.upgrade_from,old_source)
            source=case/'new-source'; shutil.copytree(PSTACK,source)
            env={**os.environ,'HOME':str(home),'CODEX_HOME':str(home/'.codex'),'CLAUDE_CONFIG_DIR':str(home/'.claude'),'DISABLE_TELEMETRY':'1'}
            run([node,cli,'add',str(old_source),'--skill','*','--agent','codex','claude-code','--copy','-y'],project,env)
            hosts=[('codex','.agents/skills','.codex/agents/poteto-agent.toml','AGENTS.md'),('claude-code','.claude/skills','.claude/agents/poteto-agent.md','CLAUDE.md')]
            for host,directory,agent_file,instruction_file in hosts:
                script=project/directory/'pstack-support/scripts/setup.py'
                (project/instruction_file).write_text('Project-owned instructions.\n')
                command=['python3',str(script),'--host',host,'--project',str(project),'--source-commit','a'*40,'--write','--benny']
                run(command,project,env)
                agent=project/agent_file
                if host=='codex': agent.write_text(agent.read_text()+'model = "user-model"\nmodel_reasoning_effort = "high"\n')
                else: agent.write_text(agent.read_text().replace('model: inherit','model: user-model\npermissionMode: default\ntools: Read, Glob, Grep'))
                checksum=hashlib.sha256(agent.read_bytes()).hexdigest()
                run(command+['--accept-merge',agent_file+'='+checksum],project,env)
                instructions=project/instruction_file
                instructions.write_text(instructions.read_text().replace('<!-- pstack:end -->','pstack-role how explorer: user-model\n<!-- pstack:end -->'))
            config=project/'.pstack/benny/configuration.yaml'; config.parent.mkdir(); config.write_text('user-owned: true\n')
            custom=project/'.pstack/automations/benny/custom.txt'; custom.write_text('keep this destination-only file')
            run([node,cli,'add',str(source),'--skill','*','--agent','codex','claude-code','--copy','-y'],project,env)
            # skills add does not uninstall retired names; exercise the documented removal.
            run([node,cli,'remove','pstack-support','--agent','codex','claude-code','-y'],project,env)
            shutil.rmtree(old_source); shutil.rmtree(source)
            for host,directory,agent_file,instruction_file in hosts:
                skills=project/directory
                assert len(list(skills.iterdir()))==54 and not (skills/'pstack-support').exists()
                before=tree(skills)
                run(['python3',str(skills/'setup-pstack/scripts/setup.py'),'--host',host,'--project',str(project),'--source-commit','b'*40,'--write','--benny'],project,env)
                assert before==tree(skills)
                agent=(project/agent_file).read_text(); instructions=(project/instruction_file).read_text()
                assert 'user-model' in agent and 'Project-owned instructions.' in instructions and 'pstack-role how explorer: user-model' in instructions
                assert 'model_reasoning_effort = "high"' in agent if host=='codex' else 'tools: Read, Glob, Grep' in agent and 'permissionMode: default' in agent
                receipt=json.loads((project/f'.pstack/setup-{host}.json').read_text())
                assert receipt['source_commit']=='b'*40 and 'setup_manifest_sha256' in receipt and 'support_manifest_sha256' not in receipt
            assert config.read_text()=='user-owned: true\n' and custom.read_text()=='keep this destination-only file'
            rows.append({'host':'codex+claude-code','case':'upgrade-retired-support-carrier','old_count':55,'count':54,'models_permissions_and_receipts_preserved':True,'user_config_and_pack_files_preserved':True,'installed_hash_unchanged':True})
            print('PASS old support layout → setup carrier, both hosts retain user configuration',flush=True)
    if args.output: args.output.write_text(json.dumps({'skills_cli':version,'rows':rows,'native_agent_loading':'not tested by this installer harness','external_automation':'not tested'},indent=2)+'\n')

if __name__=='__main__': main()
