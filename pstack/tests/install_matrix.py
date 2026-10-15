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
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--node',required=True,type=Path); parser.add_argument('--cli',required=True,type=Path); parser.add_argument('--bun',type=Path); parser.add_argument('--output',type=Path); args=parser.parse_args()
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
                        assert 'Found 55 skills' in listed,listed
                        for forbidden in ['triage-issue-reports\n','reproduce-and-fix-issues\n','setup-benny\n']: assert forbidden not in listed
                        selected=['*'] if selection=='full' else ['setup-pstack','Poteto Mode','pstack-support']
                        command=[node,cli,'add',str(source),'--skill',*selected,'--agent',host,'-y','--json']
                        if scope=='global': command+=['--global']
                        if mode=='copy': command+=['--copy']
                        result=run(command,project,env)
                        installed_base=home if scope=='global' else project
                        skills=installed_base/('.agents/skills' if host=='codex' else '.claude/skills')
                        support=skills/'pstack-support'; assert support.is_dir(),result.stdout
                        installed_names={p.name for p in skills.iterdir() if p.is_dir()}
                        expected=55 if selection=='full' else 3
                        assert len(installed_names)==expected,(name,installed_names)
                        assert not {'setup-benny','triage-issue-reports','reproduce-and-fix-issues'} & installed_names
                        script=support/'scripts/setup.py'
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
        assert (project/'.claude/skills/pstack-support').resolve()==(project/'.agents/skills/pstack-support').resolve()
        rows.append({'host':'codex+claude-code','mode':'shared-links','count':55,'source_removed':True})
        print('PASS multi-host shared links',flush=True)
    if args.output: args.output.write_text(json.dumps({'skills_cli':version,'rows':rows,'native_agent_loading':'not tested by this installer harness','external_automation':'not tested'},indent=2)+'\n')

if __name__=='__main__': main()
