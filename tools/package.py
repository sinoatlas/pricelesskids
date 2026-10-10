"""创建仅含项目公共文件的ZIP、SHA256和发布清单。"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES=['README.md','CONTRIBUTING.md','CHANGELOG.md','LICENSE.md','LICENSE-CODE','.gitignore','.nojekyll','index.html']
PUBLIC_DIRS=['book','docs','tools']
DATA_FILES=['data/guide.json','data/budget.example.json']
GITHUB_FILES=['.github/ISSUE_TEMPLATE/correction.md','.github/workflows/validate.yml']
def public_files():
    files=[ROOT/name for name in ROOT_FILES+DATA_FILES+GITHUB_FILES if (ROOT/name).is_file()]
    for dirname in PUBLIC_DIRS:
        for path in (ROOT/dirname).rglob('*'):
            if not path.is_file(): continue
            rel=path.relative_to(ROOT)
            if '__pycache__' in rel.parts or path.suffix=='.pyc': continue
            if path.name.endswith('.private.json') or path.name.startswith('.env'): continue
            if path.suffix.lower() in {'.md','.json','.py','.html','.yml','.yaml'}: files.append(path)
    return sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
def main():
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    target=out/'pricelesskids-jiangsu-v1.0.0.zip'
    records=[]
    with ZipFile(target,'w',compression=ZIP_DEFLATED) as archive:
        for p in public_files():
            raw=p.read_bytes();rel=p.relative_to(ROOT).as_posix()
            archive.writestr(rel,raw)
            records.append(dict(path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    (out/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    (out/'SHA256SUMS.txt').write_text(digest+'  '+target.name+'\n',encoding='ascii')
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist())==sorted(r['path'] for r in records)
    print(f'Packaged {len(records)} public files, {target.stat().st_size} bytes; ZIP CRC verified.')
    print(target)
    print('SHA256:',digest)
if __name__=='__main__':main()
