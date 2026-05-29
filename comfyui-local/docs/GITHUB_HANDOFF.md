# GitHub 交接说明

更新时间：2026-05-29

## 当前状态

`/Users/a1234/Documents/智能化办公` 当前不是 Git 仓库。

`/Users/a1234/Documents/comfy/ComfyUI` 是 ComfyUI 官方源码仓库，远端为：

`https://github.com/comfyanonymous/ComfyUI`

不要把本机配置、模型清单、启动脚本提交到 ComfyUI 官方仓库。

本交接包已作为独立 Git 仓库保存在：

`/Users/a1234/Documents/智能化办公/comfyui-local`

已推送到 GitHub：

`https://github.com/zhoudianfeng51-a11y/zhouzhouyuanqu12`

注意：这是独立仓库，不要再推到 `zhouzhouyuanqu` 主项目里。

## GitHub 保存范围

该分支只保存：

- `comfyui-local/start_comfyui.sh`
- `comfyui-local/stop_comfyui.sh`
- `comfyui-local/comfy_bridge.py`
- `comfyui-local/Start ComfyUI.command`
- `comfyui-local/README.md`
- `comfyui-local/docs/*.md`

不要保存：

- `.venv-comfyui-py312`
- `logs`
- `*.pid`
- `last_txt2img_workflow.json`
- ComfyUI `models`
- ComfyUI `output`
- ComfyUI `temp`

## 建议 .gitignore

```gitignore
comfyui-local/.venv-comfyui*/
comfyui-local/logs/
comfyui-local/*.pid
comfyui-local/last_txt2img_workflow.json
*.png
*.jpg
*.jpeg
*.webp
*.safetensors
*.ckpt
*.pth
*.bin
*.onnx
```

## 推送前检查

推送前确认：

1. 文档里没有 API Key。
2. 文档里没有私人账号密码。
3. 没有模型文件。
4. 没有生成图片。
5. 没有 Python 虚拟环境。

## 后续同步命令

本地修改后执行：

```bash
cd /Users/a1234/Documents/智能化办公/comfyui-local
git add .gitignore README.md "Start ComfyUI.command" comfy_bridge.py docs start_comfyui.sh stop_comfyui.sh
git commit -m "Update ComfyUI local handoff"
git push
```
