# ComfyUI 人物稳定多视图环境交接

更新时间：2026-05-29

## 目标

本目录记录本机 ComfyUI 的启动、插件、模型和后续开发边界，避免以后重复安装、模型乱放、环境版本漂移。

当前目标收窄为：

1. 人物生成时尽量保持同一个身份。
2. 支持参考人脸锁定。
3. 支持姿态/角度控制。
4. 为后续人物多视图工作流做准备。

## 本机路径

ComfyUI 主目录：

`/Users/a1234/Documents/comfy/ComfyUI`

本地启动和自动化桥接目录：

`/Users/a1234/Documents/智能化办公/comfyui-local`

桌面启动器：

`/Users/a1234/Desktop/Start-ComfyUI.command`

输出目录：

`/Users/a1234/Documents/comfy/ComfyUI/output`

## 当前硬件与运行环境

ComfyUI 启动日志识别：

- 系统：macOS / Darwin
- 设备：MPS
- 统一内存：16GB
- Python：3.12.13
- PyTorch：2.12.0
- ComfyUI：0.22.0

磁盘状态快照：

- ComfyUI 总占用：约 8.7GB
- ComfyUI models 占用：约 8.4GB
- 本地启动环境占用：约 3.4GB
- 可用磁盘：约 675GB

## 已安装插件

插件安装位置：

`/Users/a1234/Documents/comfy/ComfyUI/custom_nodes`

已安装：

- `comfyui-ipadapter`
- `comfyui-controlnet-aux`
- `ComfyUI-MVAdapter`

已验证 ComfyUI 能正常加载：

- `IPAdapterUnifiedLoaderFaceID`
- `ControlNetLoader`
- `CLIPVisionLoader`
- `ComfyUI-MVAdapter` 节点

## 已安装模型

基础模型：

`/Users/a1234/Documents/comfy/ComfyUI/models/checkpoints/v1-5-pruned-emaonly.safetensors`

IPAdapter / FaceID：

`/Users/a1234/Documents/comfy/ComfyUI/models/ipadapter/ip-adapter-faceid-plusv2_sd15.bin`

`/Users/a1234/Documents/comfy/ComfyUI/models/ipadapter/ip-adapter-plus-face_sd15.safetensors`

FaceID LoRA：

`/Users/a1234/Documents/comfy/ComfyUI/models/loras/ip-adapter-faceid-plusv2_sd15_lora.safetensors`

CLIP Vision：

`/Users/a1234/Documents/comfy/ComfyUI/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`

ControlNet：

`/Users/a1234/Documents/comfy/ComfyUI/models/controlnet/control_v11p_sd15_openpose.pth`

InsightFace antelopev2：

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2/1k3d68.onnx`

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2/2d106det.onnx`

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2/genderage.onnx`

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2/glintr100.onnx`

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2/scrfd_10g_bnkps.onnx`

预留目录：

`/Users/a1234/Documents/comfy/ComfyUI/models/mvadapter`

`/Users/a1234/Documents/comfy/ComfyUI/models/instantid`

## 启动方式

日常使用：

1. 双击桌面 `Start-ComfyUI.command`。
2. 等终端出现 `To see the GUI go to: http://127.0.0.1:8188`。
3. 不要关闭终端窗口。
4. 打开 `http://127.0.0.1:8188`。

命令行启动：

```bash
cd /Users/a1234/Documents/智能化办公
./comfyui-local/start_comfyui.sh
```

命令行停止：

```bash
cd /Users/a1234/Documents/智能化办公
./comfyui-local/stop_comfyui.sh
```

注意：在 Codex 受限执行环境中，后台 daemon 模式可能在命令结束后被系统回收。桌面双击启动器是推荐方式。

## 自动化桥接

桥接脚本：

`/Users/a1234/Documents/智能化办公/comfyui-local/comfy_bridge.py`

检查服务：

```bash
./comfyui-local/comfy_bridge.py status
```

列出基础模型：

```bash
./comfyui-local/comfy_bridge.py checkpoints
```

基础文生图烟测：

```bash
./comfyui-local/comfy_bridge.py txt2img \
  --prompt "a simple clean product photo of a white backpack on a white background, studio lighting" \
  --negative "low quality, blurry, text, watermark" \
  --width 512 \
  --height 512 \
  --steps 8 \
  --cfg 6 \
  --prefix codex_smoke
```

已验证输出样例：

`/Users/a1234/Documents/comfy/ComfyUI/output/codex_smoke_00001_.png`

## 当前可做的稳定人物路线

第一阶段已具备：

- SD1.5 基础模型
- IPAdapter FaceID plus v2 身份锁定
- FaceID LoRA
- CLIP Vision
- InsightFace antelopev2
- OpenPose ControlNet

适合先做：

1. 单张参考脸锁定。
2. 固定姿态或角度。
3. 正面、侧面、背面等分步生成。
4. 用固定 seed、固定 prompt、固定参数降低漂移。

不建议一开始做：

1. 一次性 6-8 视图。
2. SDXL + MVAdapter + ControlNet + FaceID 全部同时开启。
3. 高分辨率批量生成。

## 第二阶段待补

如果要真正使用 MVAdapter 的 SDXL 多视图能力，还需要下载：

1. SDXL base checkpoint。
2. `mvadapter_i2mv_sdxl_beta.safetensors`。
3. `sdxl_vae.safetensors` 或兼容 VAE。

风险：

- 单个 MVAdapter i2mv beta 约 3.6GB。
- SDXL 主模型约 6-7GB。
- 16GB Mac 可以尝试，但需要小视图数量、低并发、低分辨率。

建议：

先用当前 SD1.5 + FaceID + OpenPose 跑稳定身份，再决定是否升级 SDXL MVAdapter。

## 不要做的事

- 不要把本地文档提交到 `/Users/a1234/Documents/comfy/ComfyUI` 的官方 `origin`。
- 不要把模型文件提交到 GitHub。
- 不要把 `.venv-comfyui-py312` 提交到 GitHub。
- 不要把 output、temp、日志、pid 文件提交到 GitHub。
- 不要重复安装旧版或来源不明的 IPAdapter / ControlNet 插件。

