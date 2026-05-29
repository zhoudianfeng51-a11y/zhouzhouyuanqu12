# 本地 ComfyUI 自动化入口

这套小工具固定连接你的本机 ComfyUI：

`/Users/a1234/Documents/comfy/ComfyUI`

## 交接文档

后续继续开发前，先读：

`comfyui-local/docs/HANDOFF.md`

`comfyui-local/docs/MODEL_MANIFEST.md`

`comfyui-local/docs/WORKFLOW_PLAN.md`

`comfyui-local/docs/GITHUB_HANDOFF.md`

注意：不要把模型、输出图片、虚拟环境、日志提交到 GitHub。

## 一键启动

双击：

`comfyui-local/Start ComfyUI.command`

或者在当前目录运行：

```bash
./comfyui-local/start_comfyui.sh
```

首次运行会优先用本机 Python 3.12，在 `comfyui-local/.venv-comfyui-py312` 创建本地 Python 环境，并安装 ComfyUI 依赖。后续会直接启动：

`http://127.0.0.1:8188`

默认是前台常驻启动，窗口保持打开时 ComfyUI 才保持在线。需要后台尝试时可以运行：

```bash
./comfyui-local/start_comfyui.sh --daemon
```

## 停止服务

```bash
./comfyui-local/stop_comfyui.sh
```

## 我和 ComfyUI 打通

检查服务：

```bash
./comfyui-local/comfy_bridge.py status
```

查看可用大模型：

```bash
./comfyui-local/comfy_bridge.py checkpoints
```

提交一次基础文生图：

```bash
./comfyui-local/comfy_bridge.py txt2img \
  --prompt "a clean product photo of a white backpack, studio lighting, white background" \
  --prefix codex_test
```

生成结果会输出到：

`/Users/a1234/Documents/comfy/ComfyUI/output`

## 当前能力

当前本机已发现的基础模型：

`v1-5-pruned-emaonly.safetensors`

已补齐第一阶段人物稳定套装：

- IPAdapter FaceID plus v2
- FaceID LoRA
- CLIP Vision
- InsightFace antelopev2
- OpenPose ControlNet
- MVAdapter 节点代码

现在可先做参考脸锁定、姿态控制和分步人物多视图。SDXL MVAdapter 权重仍属于第二阶段。
