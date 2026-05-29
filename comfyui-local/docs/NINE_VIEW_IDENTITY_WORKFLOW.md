# 人物 9 视图标准工作流落地说明

更新时间：2026-05-29

## 当前目标

搭建一套稳定、可复用、可审核的人物 9 视图身份卡生产线。

当前阶段不追求一次性批量出 9 张成片，而是先保证：

1. 不走 CPU。
2. 不跳阶段。
3. 不把服装写死为最终造型。
4. 每张图都有独立候选、审核、冻结、交付路径。
5. 后续可换任意服装。

## 核心原则

优先级固定为：

```text
身份一致性 > 角度准确性 > 身体比例 > 结构完整性 > 美观性
```

服装只作为占位服，用于观察身体比例、结构和站姿。最终换装任务另做，不依赖占位服款式。

## 本机参考图

ComfyUI 输入目录：

`/Users/a1234/Documents/comfy/ComfyUI/input`

当前工作流使用：

```text
person_face_front_lock.png
person_face_left45.png
person_face_right45.png
person_fullbody_outfit_front.png
```

说明：

- `person_face_front_lock.png`：正面身份锚点。
- `person_face_left45.png`：左 45 度头脸角度锚点。
- `person_face_right45.png`：右 45 度头脸角度锚点。
- `person_fullbody_outfit_front.png`：仅用于正面全身姿态和比例参考，不作为最终服装锁定。

## 输出目录

标准项目目录：

`/Users/a1234/Documents/comfy/ComfyUI/output/人物九视图工作流`

结构：

```text
人物九视图工作流/
├─ 00_输入参考/
├─ 01_头脸锁脸/
├─ 02_全身结构/
├─ 03_过程版本/
├─ 04_冻结母版/
└─ 05_最终交付/
```

## 执行器

脚本：

`comfyui-local/nine_view_identity_workflow.py`

查看 9 视图计划：

```bash
./comfyui-local/nine_view_identity_workflow.py plan
```

创建目录并复制参考图：

```bash
./comfyui-local/nine_view_identity_workflow.py init
```

只生成 9 个工作流 JSON，不跑图：

```bash
./comfyui-local/nine_view_identity_workflow.py build-all
```

只跑某一个视图候选：

```bash
./comfyui-local/nine_view_identity_workflow.py run --view 01
```

冻结审核通过的候选图：

```bash
./comfyui-local/nine_view_identity_workflow.py freeze --view 01 --src /path/to/approved.png
```

## 强制执行顺序

第一组：头脸锁脸

```text
01_正面锁脸
02_左四十五度锁脸
03_右四十五度锁脸
```

第二组：正面全身比例母版

```text
04_正面全身
```

第三组：全身角度补齐

```text
05_左四十五度全身
06_右四十五度全身
07_左侧面全身
08_右侧面全身
09_背面全身
```

没有冻结 `01-03`，不要进入全身阶段。

没有冻结 `04`，不要进入 `05-09`。

## 运行保护

执行器在 `run` 时会检查：

1. ComfyUI 是否在线。
2. ComfyUI 当前设备是否为 `mps`。
3. 必要参考图是否存在。

未通过时会停止，不提交出图任务。

## 当前能力边界

当前已具备：

- SD1.5 基础模型。
- IPAdapter FaceID plus v2。
- CLIP Vision。
- OpenPose ControlNet。
- Apple MPS 运行环境。

当前未把 `05-09` 做成强姿态骨架控制，因为还没有对应的 45 度、侧面、背面全身姿态参考图。现阶段 `05-09` 先作为候选生成入口，正式冻结前必须人工审核，必要时补姿态参考图后再增强。
