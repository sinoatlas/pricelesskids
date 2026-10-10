# 上传与发布

目标仓库：[sinoatlas/pricelesskids](https://github.com/sinoatlas/pricelesskids)。

**本地文件已经生成，不等于已经上传。** 上传器只有在远端提交并核对全部所选文件的Git对象后，才打印 `UPLOADED AND VERIFIED` 并生成 `outputs/publication.json`。没有该记录时，不宣称远端已发布。网页阅读器的Pages地址也只在实际启用并部署成功后可访问。

## 已登录GitHub网页时

打开仓库的 **Add file → Upload files**，将项目公开文件和 `book/`、`docs/`、`data/`、`tools/`目录按原结构上传；必要时分批。仅上传ZIP会把ZIP保存为一个文件，不会自动展开成项目目录。

不要上传 `outputs/`、`__pycache__/`、任何真实家庭数据、`.env`、访问令牌、浏览器资料、`.local/`或缓存。发布包ZIP只含白名单公共文件，解压后保留目录结构即可。

若仓库已有同名文件，先对比内容；本项目不会自动清空或覆盖用户其他文件。上传后查看README、16个章节、来源台账、13市索引和index.html，确认文件名与目录正确。

## 可选标准库上传器

现有本地GitHub认证可通过GH_TOKEN或GITHUB_TOKEN提供；若没有环境变量，可在自己的终端隐藏输入已有令牌。**不要把令牌发送到聊天或写进代码。** 网页登录不会自动给Python进程API写权限，二者认证独立。

```console
python tools/build.py
python tools/check.py
python tools/publish.py --dry-run
python tools/publish.py --repository sinoatlas/pricelesskids
```

使用已有具有目标仓库内容写权限的凭据；无需为了阅读指南创建令牌。发布脚本不创建仓库、不设置公开私密、不删除其他路径、不改用户权限、不强推。它会读取现有分支头，冲突时停止；空仓库创建首提交，有现有内容则在其上增加提交。

默认不上传 `.github/workflows/`，降低对已有凭据工作流权限的要求；如确定希望发布自动检查且已有相应权限，可以增加 `--include-workflows`。Issue模板仍在默认公开白名单中。需要替换远端同名不同内容时，在审阅远端差异后显式增加 `--replace`；不要盲目使用。

上传失败可能留下未被分支引用的Git对象，但不会自动改变分支。分支更新后如验证失败，脚本会明确报告“已提交但未完成验证”，请查看实际仓库。

## GitHub Pages可选

本项目无需在线部署即可使用：直接打开index.html。若希望仓库同时提供在线检索页，可在GitHub仓库Settings → Pages中按当前界面选择从默认分支根目录发布。Pages是否可用取决于仓库权限与GitHub设置，上传器不会自动启用。

预期地址为 `https://sinoatlas.github.io/pricelesskids/`，不在未核验前宣传为已上线。
