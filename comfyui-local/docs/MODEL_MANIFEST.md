# 模型清单

更新时间：2026-05-29

## 已安装模型

| 类别 | 文件 | 目录 | 大小 |
| --- | --- | --- | --- |
| SD1.5 checkpoint | `v1-5-pruned-emaonly.safetensors` | `models/checkpoints` | 4.0GB |
| CLIP Vision | `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | `models/clip_vision` | 2.4GB |
| FaceID | `ip-adapter-faceid-plusv2_sd15.bin` | `models/ipadapter` | 149MB |
| IPAdapter face | `ip-adapter-plus-face_sd15.safetensors` | `models/ipadapter` | 94MB |
| FaceID LoRA | `ip-adapter-faceid-plusv2_sd15_lora.safetensors` | `models/loras` | 49MB |
| ControlNet OpenPose | `control_v11p_sd15_openpose.pth` | `models/controlnet` | 1.3GB |
| InsightFace | `1k3d68.onnx` | `models/insightface/models/antelopev2` | 137MB |
| InsightFace | `2d106det.onnx` | `models/insightface/models/antelopev2` | 4.8MB |
| InsightFace | `genderage.onnx` | `models/insightface/models/antelopev2` | 1.3MB |
| InsightFace | `glintr100.onnx` | `models/insightface/models/antelopev2` | 249MB |
| InsightFace | `scrfd_10g_bnkps.onnx` | `models/insightface/models/antelopev2` | 16MB |

## 模型目录规范

大模型：

`/Users/a1234/Documents/comfy/ComfyUI/models/checkpoints`

IPAdapter：

`/Users/a1234/Documents/comfy/ComfyUI/models/ipadapter`

FaceID LoRA：

`/Users/a1234/Documents/comfy/ComfyUI/models/loras`

CLIP Vision：

`/Users/a1234/Documents/comfy/ComfyUI/models/clip_vision`

ControlNet：

`/Users/a1234/Documents/comfy/ComfyUI/models/controlnet`

InsightFace：

`/Users/a1234/Documents/comfy/ComfyUI/models/insightface/models/antelopev2`

MVAdapter：

`/Users/a1234/Documents/comfy/ComfyUI/models/mvadapter`

InstantID：

`/Users/a1234/Documents/comfy/ComfyUI/models/instantid`

## 第二阶段候选模型

这些模型尚未安装：

| 用途 | 文件 |
| --- | --- |
| SDXL 主模型 | `sd_xl_base_1.0.safetensors` |
| SDXL VAE | `sdxl_vae.safetensors` |
| MVAdapter 图生多视图 | `mvadapter_i2mv_sdxl_beta.safetensors` |

安装前应确认：

- 是否确实需要 SDXL 多视图。
- 是否接受更慢的运行速度。
- 是否先备份当前可用环境。

