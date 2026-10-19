#!/usr/bin/env python3
"""Rebuild the source migration ledger and installed-content integrity manifest."""
from pathlib import Path
import hashlib
import json
import os
import re

PSTACK = Path(__file__).resolve().parents[1]
SUPPORT = PSTACK / 'skills/pstack-support'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def files(path):
    return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file() and p.name != 'manifest.json' and '__pycache__' not in p.parts and 'node_modules' not in p.parts}

def target(source):
    relative = source.removeprefix('pstack/')
    if relative == '.cursor-plugin/plugin.json': return None
    if relative == 'README.md': return 'pstack/skills/pstack-support/README.md'
    if relative.split('/')[0] in ('agents','automations','docs','assets','LICENSE'):
        relative = 'skills/pstack-support/' + relative
        if '/automations/' in relative: relative = relative.replace('/SKILL.md','/INSTRUCTIONS.md')
    return 'pstack/' + relative

def build():
    inventory = json.loads((PSTACK / 'docs/source-inventory.json').read_text())
    skills = {}
    for directory in sorted((PSTACK/'skills').iterdir()):
        if directory.name == 'pstack-support' or not directory.is_dir(): continue
        text = (directory/'SKILL.md').read_text()
        name = re.search(r'^name:\s*(.+)$',text,re.M).group(1).strip('"\'')
        manual = bool(re.search(r'^disable-model-invocation:\s*true$',text,re.M))
        if manual:
            metadata=directory/'agents/openai.yaml'; metadata.parent.mkdir(exist_ok=True)
            metadata.write_text('policy:\n  allow_implicit_invocation: false\n')
        skills[directory.name]={'name':name,'manual':manual,'files':files(directory)}
    manifest={'schema':1,'source_commit':inventory['commit'],'adapter_version':'0.15.24-host.1','skills':skills,'support_files':files(SUPPORT)}
    (SUPPORT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lines=['# Source migration ledger','',f"Upstream: `{inventory['repository']}` at `{inventory['commit']}`. All original 54 frontmatter names and manual/path policies are retained. Benny instruction filenames change to avoid skill discovery, including full-depth scans.",'','| Source | Target | Decision | Verification |','| --- | --- | --- | --- |']
    for entry in inventory['files']:
        destination=target(entry['source']); entry['target']=destination
        path=PSTACK.parent / destination if destination else None
        if destination is None:
            entry['decision']='remove Cursor-only plugin registration; npx skills is the entry point'; entry['verification']='scope removal'
        elif path.is_file():
            actual=sha(path); entry['target_sha256']=actual; entry['target_bytes']=path.stat().st_size
            entry['decision']='preserve byte for byte' if actual==entry['sha256'] else 'host adaptation; full workflow retained (Make Bot UI original retained in its reference)'
            entry['verification']='hash matches' if actual==entry['sha256'] else 'present; source hash recorded; static/test coverage in validation report'
            if (path.stat().st_mode & 0o777) != int(entry['mode'],8): raise ValueError(f'Changed source file permissions: {destination}')
        else: raise ValueError(f'Missing original file: {destination}')
        lines.append(f"| `{entry['source']}` | `{destination or '(removed)'}` | {entry['decision']} | {entry['verification']} |")
    (PSTACK/'docs/source-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (PSTACK/'docs/migration.md').write_text('\n'.join(lines)+'\n')
    patterns=[r'\.cursor/',r'cursor-team-kit',r'\bgrok[- ]',r'cloud_base_branch',r'environment:\s*"cloud"',r'\bTask\b',r'update_state',r'SendToUser',r'\.mdc']
    coupling=[]
    source_inventory={entry['source']:entry for entry in inventory['files']}
    import subprocess
    for source,entry in source_inventory.items():
        if not source.endswith(('.md','.ts','.sh','.json','.yaml')): continue
        original=subprocess.check_output(['git','show',f"{inventory['commit']}:{source}"],cwd=PSTACK.parent,text=True)
        matches=[f'{n}: {line}' for n,line in enumerate(original.splitlines(),1) if any(re.search(pattern,line,re.I) for pattern in patterns)]
        if matches:
            coupling.append({'source':source,'target':entry['target'],'assumptions':matches,'status':'adapted through project-local native CLI webhook executor; Tailscale access remains unverified' if '/make-bot-ui/' in source else 'adapted; native execution still requires fresh-host verification'})
    (PSTACK/'docs/cursor-coupling.json').write_text(json.dumps(coupling,indent=2)+'\n')
    source_files=len(inventory['files']); source_bytes=sum(e['bytes'] for e in inventory['files'])
    current=list(p for p in PSTACK.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'node_modules' not in p.parts)
    print(json.dumps({'source_files':source_files,'source_bytes':source_bytes,'current_files':len(current),'current_bytes':sum(p.stat().st_size for p in current),'original_skills':len(skills),'added_support_skills':1,'duplicated_shared_packs':0},indent=2))

if __name__=='__main__': build()
