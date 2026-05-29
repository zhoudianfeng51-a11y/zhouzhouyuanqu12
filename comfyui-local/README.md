# 本地 ComfyUI 自动化入口

这套小工具固定连接你的本机 ComfyUI：

`/Users/a1234/Documents/comfy/ComfyUI`

## 交接文档

后续继续开发前，先读：

`comfyui-local/docs/HANDOFF.md`

`comfyui-local/docs/MODEL_MANIFEST.md`

`comfyui-local/docs/WORKFLOW_PLAN.md`

`comfyui-local/docs/GITHUB_HANDOFF.md`

`comfyui-local/docs/NINE_VIEW_IDENTITY_WORKFLOW.md`

注意：不要把模型、输出图片、虚拟环境、日志提交到 GitHub。

## 一键启动

双击：

`/Users/a1234/Desktop/壹源万象 ComfyUI.app`

备用启动器：

`/Users/a1234/Desktop/Start-ComfyUI.command`

或者在当前目录运行：

```bash
./comfyui-local/start_comfyui.sh
```

首次运行会优先用本机 Python 3.12，在 `comfyui-local/.venv-comfyui-py312` 创建本地 Python 环境，并安装 ComfyUI 依赖。后续会直接启动：

`http://127.0.0.1:8188`

默认是前台常驻启动，窗口保持打开时 ComfyUI 才保持在线。启动脚本会先检查 Apple MPS，未检测到 MPS 时会拒绝启动，避免误用 CPU 跑图。服务启动成功后会自动打开：

`http://127.0.0.1:8188`

需要后台尝试时可以运行：

```bash
./comfyui-local/start_comfyui.sh --daemon
```

正式出图不要使用 `COMFYUI_ALLOW_CPU=1`。这个开关只用于临时诊断。

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

## 人物 9 视图标准工作流

执行器：

```bash
./comfyui-local/nine_view_identity_workflow.py plan
./comfyui-local/nine_view_identity_workflow.py build-all
./comfyui-local/nine_view_identity_workflow.py run --view 01
```

标准输出目录：

`/Users/a1234/Documents/comfy/ComfyUI/output/人物九视图工作流`

原则：先冻结 `01-03` 头脸锁脸，再做 `04` 正面全身，最后补 `05-09`。服装只作为占位服，不作为最终造型锁定。

## 已验证运行状态

2026-05-29 已验证：

- PyTorch：`2.6.0`
- ComfyUI 设备：`mps`
- 服务地址：`http://127.0.0.1:8188`
- CPU 模式保护：已开启

注意：Codex 普通受限执行环境可能无法访问 Apple MPS。日常使用请从桌面启动器或授权前台环境启动。
