"""可选GitHub REST上传器；无Git依赖。未认证时只提示，不虚报上传完成。

只发布package.public_files()的白名单；保存旧分支头，拒绝隐式覆盖。
认证从GH_TOKEN / GITHUB_TOKEN读取，或本地getpass输入；不保存或输出令牌。
"""
from pathlib import Path
import argparse
import base64
import getpass
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from urllib.parse import quote
from package import public_files, ROOT

def git_sha(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',default='sinoatlas/pricelesskids')
    parser.add_argument('--dry-run',action='store_true',help='只列本地发布文件，不访问GitHub')
    parser.add_argument('--replace',action='store_true',help='允许替换同路径不同内容；原提交仍保留')
    parser.add_argument('--include-workflows',action='store_true',help='包含GitHub Actions文件，令牌可能另需工作流权限')
    args=parser.parse_args()
    if not __import__('re').fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',args.repository):
        parser.error('repository must be owner/name')
    files=[p for p in public_files() if args.include_workflows or '.github/workflows/' not in p.relative_to(ROOT).as_posix()]
    if args.dry_run:
        for p in files: print(p.relative_to(ROOT).as_posix())
        print(f'DRY RUN ONLY: {len(files)} files; no authentication, network or upload.')
        return
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        if not sys.stdin.isatty(): raise SystemExit('Authentication required; no files uploaded. Use an existing GitHub credential in a local terminal; never paste tokens in chat.')
        token=getpass.getpass('Existing GitHub token (hidden input, never saved): ').strip()
    if not token: raise SystemExit('Empty credential; no files uploaded.')
    base='https://api.github.com/repos/'+args.repository
    def api(method,path,data=None,allowed=()):
        url=base+path
        body=None if data is None else json.dumps(data).encode('utf-8')
        req=urllib.request.Request(url,data=body,method=method,headers={
            'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'pricelesskids-publisher',
            'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                raw=r.read();return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in allowed: return None
            # 仅记录状态和API路径，绝不打印请求头或token。
            raise RuntimeError(f'GitHub API {method} {path}: HTTP {e.code}') from None
    repo=api('GET','')
    if not repo.get('permissions',{}).get('push',False):
        raise SystemExit('Credential has no write access to target repository; no files uploaded.')
    branch=repo['default_branch']
    ref=api('GET','/git/ref/heads/'+quote(branch,safe=''),allowed=(404,409))
    previous=ref['object']['sha'] if ref else None
    previous_tree=None;existing={}
    if previous:
        commit=api('GET','/git/commits/'+previous);previous_tree=commit['tree']['sha']
        tree=api('GET','/git/trees/'+previous_tree+'?recursive=1')
        if tree.get('truncated'): raise SystemExit('Remote tree truncated; refusing incomplete conflict review.')
        existing={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
    paths={p.relative_to(ROOT).as_posix():p for p in files}
    conflicts=[name for name,p in paths.items() if name in existing and existing[name]!=git_sha(p.read_bytes())]
    if conflicts and not args.replace:
        print('Existing differing files; upload stopped before creating blobs:')
        print('\n'.join(conflicts))
        raise SystemExit('Review remote files first; --replace explicitly allows replacements without deleting other remote paths.')
    changes=[]
    for name,p in paths.items():
        raw=p.read_bytes()
        if existing.get(name)==git_sha(raw): continue
        blob=api('POST','/git/blobs',dict(content=base64.b64encode(raw).decode('ascii'),encoding='base64'))
        changes.append(dict(path=name,mode='100644',type='blob',sha=blob['sha']))
    if not changes:
        print('All selected files already match remote; no new commit.')
        return
    tree_body=dict(tree=changes)
    if previous_tree: tree_body['base_tree']=previous_tree
    new_tree=api('POST','/git/trees',tree_body)
    new_commit=api('POST','/git/commits',dict(message='Publish Jiangsu parenting guide v1.0.0',tree=new_tree['sha'],parents=[previous] if previous else []))
    if previous:
        api('PATCH','/git/refs/heads/'+quote(branch,safe=''),dict(sha=new_commit['sha'],force=False))
    else:
        api('POST','/git/refs',dict(ref='refs/heads/'+branch,sha=new_commit['sha']))
    current=api('GET','/git/ref/heads/'+quote(branch,safe=''))
    if current['object']['sha']!=new_commit['sha']:
        raise RuntimeError('Committed, but branch changed during verification; inspect remote history.')
    verified=api('GET','/git/trees/'+new_tree['sha']+'?recursive=1')
    if verified.get('truncated'): raise RuntimeError('Committed, but verification tree truncated; verify repository manually.')
    actual={x['path']:x['sha'] for x in verified['tree'] if x['type']=='blob'}
    bad=[n for n,p in paths.items() if actual.get(n)!=git_sha(p.read_bytes())]
    if bad: raise RuntimeError('Committed, but file verification failed: '+', '.join(bad))
    record=dict(repository=args.repository,branch=branch,commit=new_commit['sha'],previous=previous,verified_files=len(paths),url='https://github.com/'+args.repository+'/commit/'+new_commit['sha'])
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    (out/'publication.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('UPLOADED AND VERIFIED:',record['url'])
if __name__=='__main__': main()
