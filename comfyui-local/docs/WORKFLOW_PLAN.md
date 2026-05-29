# 人物稳定多视图工作流计划

更新时间：2026-05-29

## 当前可落地流程

第一版先不追求“一键 MVAdapter 全自动多视图”，先追求身份稳定。

推荐节点链路：

1. `Load Checkpoint`
2. `Load Image` 读取人物参考图
3. `IPAdapter Unified Loader FaceID`
4. `Apply IPAdapter FaceID`
5. `OpenPose Preprocessor`
6. `Load ControlNet Model`
7. `Apply ControlNet`
8. `CLIP Text Encode`
9. `KSampler`
10. `VAE Decode`
11. `Save Image`

## 稳定参数建议

身份稳定优先：

- FaceID preset：`FACEID PLUS V2`
- LoRA strength：从 `0.6` 起试
- IPAdapter weight：从 `0.8` 起试
- CFG：`5.5-7`
- steps：`20-30`
- seed：固定
- 分辨率：先 `512x768` 或 `512x512`

负面提示词建议：

`different person, changed face, inconsistent identity, asymmetrical face, bad anatomy, extra limbs, blurry, low quality, watermark, text`

## 多视图策略

建议分三步，而不是一次全自动：

1. 正面视图：参考图 + 正面姿态。
2. 侧面视图：同一个参考图 + 侧面姿态。
3. 背面视图：弱化脸部要求，重点保持发型、衣服、体型。

每一步保持：

- 同一参考图。
- 同一基础 prompt。
- 同一 checkpoint。
- 同一 seed 或相邻 seed。
- 同一 FaceID 参数。

## 质量判断

每轮输出后只判断三件事：

1. 脸是否仍像同一个人。
2. 发型/衣服是否一致。
3. 姿态/角度是否符合预期。

如果脸漂：

- 提高 IPAdapter weight。
- 提高 FaceID LoRA strength，但不要直接拉满。
- 换更清晰正脸参考图。
- 降低 prompt 对五官的描述，避免和参考脸冲突。

如果姿态漂：

- 提高 ControlNet strength。
- 换更干净的 OpenPose 输入。
- 降低生成分辨率先跑通。

## 后续自动化

后续可以在 `comfy_bridge.py` 增加：

1. 自动上传参考图到 ComfyUI input。
2. 自动生成 FaceID + OpenPose 工作流 JSON。
3. 自动按正面、侧面、背面批量提交。
4. 自动整理 output 到一个项目目录。

建议自动化输出目录：

`/Users/a1234/Documents/comfy/ComfyUI/output/person-multiview/<project-name>`

