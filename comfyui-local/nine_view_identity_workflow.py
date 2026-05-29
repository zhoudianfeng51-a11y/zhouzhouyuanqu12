#!/usr/bin/env python3
"""Build and run a staged ComfyUI workflow for a 9-view character identity card.

The workflow is intentionally conservative: it creates one candidate at a time,
checks the local ComfyUI device, and refuses to continue if Apple MPS is not the
active device. It does not batch-generate all 9 views by default.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


SERVER = "http://127.0.0.1:8188"
COMFY_DIR = Path("/Users/a1234/Documents/comfy/ComfyUI")
INPUT_DIR = COMFY_DIR / "input"
OUTPUT_DIR = COMFY_DIR / "output"
PROJECT_DIR = OUTPUT_DIR / "人物九视图工作流"
WORKFLOW_DIR = Path(__file__).resolve().parent / "workflows" / "nine_view_identity"

DEFAULT_CHECKPOINT = "v1-5-pruned-emaonly.safetensors"
DEFAULT_CLIP_VISION = "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
DEFAULT_CONTROLNET = "control_v11p_sd15_openpose.pth"

REFERENCE_FILES = {
    "front_face": "person_face_front_lock.png",
    "left45_face": "person_face_left45.png",
    "right45_face": "person_face_right45.png",
    "front_fullbody": "person_fullbody_outfit_front.png",
}

NEGATIVE = (
    "different person, inconsistent identity, changed face, adult woman, older person, "
    "glamour portrait, fashion editorial, cartoon, doll face, over-smoothed skin, "
    "large round eyes, red lipstick, pointed chin, narrow cheeks, changed hairstyle, "
    "changed earrings, complex costume, logo, text, watermark, bad anatomy, extra limbs, "
    "extra fingers, missing feet, cropped feet, blurry, low quality"
)

PLACEHOLDER_OUTFIT = (
    "simple placeholder outfit for body proportion review, plain light color short sleeve top, "
    "simple plain shorts or basic lower garment, white socks, simple flat white shoes, "
    "no complex fashion styling"
)


@dataclass(frozen=True)
class ViewSpec:
    code: str
    filename: str
    stage_dir: str
    face_ref: str
    prompt: str
    width: int
    height: int
    pose_ref: str | None = None
    face_weight: float = 0.82
    lora_strength: float = 0.62
    pose_strength: float = 0.55
    steps: int = 12
    cfg: float = 6.0


VIEWS: dict[str, ViewSpec] = {
    "01": ViewSpec(
        code="01",
        filename="01_正面锁脸",
        stage_dir="01_头脸锁脸",
        face_ref=REFERENCE_FILES["front_face"],
        prompt=(
            "realistic studio head and shoulders identity reference of the same young girl, "
            "front view, neutral natural expression, long dark hair, small heart earrings, "
            "plain white background, soft clean light, natural skin texture"
        ),
        width=512,
        height=640,
        face_weight=0.92,
        lora_strength=0.72,
    ),
    "02": ViewSpec(
        code="02",
        filename="02_左四十五度锁脸",
        stage_dir="01_头脸锁脸",
        face_ref=REFERENCE_FILES["left45_face"],
        prompt=(
            "realistic studio head and shoulders identity reference of the same young girl, "
            "left 45 degree three quarter head view, both eyes visible, far eye slightly smaller, "
            "natural nose perspective, long dark hair, small heart earrings, plain white background"
        ),
        width=512,
        height=640,
        face_weight=0.88,
        lora_strength=0.68,
    ),
    "03": ViewSpec(
        code="03",
        filename="03_右四十五度锁脸",
        stage_dir="01_头脸锁脸",
        face_ref=REFERENCE_FILES["right45_face"],
        prompt=(
            "realistic studio head and shoulders identity reference of the same young girl, "
            "right 45 degree three quarter head view, both eyes visible, far eye slightly smaller, "
            "natural nose perspective, long dark hair, small heart earrings, plain white background"
        ),
        width=512,
        height=640,
        face_weight=0.88,
        lora_strength=0.68,
    ),
    "04": ViewSpec(
        code="04",
        filename="04_正面全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["front_face"],
        pose_ref=REFERENCE_FILES["front_fullbody"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, front view, "
            "standing naturally, full body visible including feet, plain white background, "
            f"{PLACEHOLDER_OUTFIT}, preserve age, hair direction, face identity and body proportion"
        ),
        width=512,
        height=768,
        face_weight=0.78,
        lora_strength=0.58,
        pose_strength=0.72,
    ),
    "05": ViewSpec(
        code="05",
        filename="05_左四十五度全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["left45_face"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, left 45 degree "
            "three quarter body view, head and body both turned left 45 degrees, full body visible "
            f"including feet, plain white background, {PLACEHOLDER_OUTFIT}"
        ),
        width=512,
        height=768,
    ),
    "06": ViewSpec(
        code="06",
        filename="06_右四十五度全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["right45_face"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, right 45 degree "
            "three quarter body view, head and body both turned right 45 degrees, full body visible "
            f"including feet, plain white background, {PLACEHOLDER_OUTFIT}"
        ),
        width=512,
        height=768,
    ),
    "07": ViewSpec(
        code="07",
        filename="07_左侧面全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["left45_face"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, pure left side "
            "profile body view, natural side silhouette, full body visible including feet, plain "
            f"white background, {PLACEHOLDER_OUTFIT}"
        ),
        width=512,
        height=768,
        face_weight=0.62,
        lora_strength=0.45,
    ),
    "08": ViewSpec(
        code="08",
        filename="08_右侧面全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["right45_face"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, pure right side "
            "profile body view, natural side silhouette, full body visible including feet, plain "
            f"white background, {PLACEHOLDER_OUTFIT}"
        ),
        width=512,
        height=768,
        face_weight=0.62,
        lora_strength=0.45,
    ),
    "09": ViewSpec(
        code="09",
        filename="09_背面全身",
        stage_dir="02_全身结构",
        face_ref=REFERENCE_FILES["front_face"],
        prompt=(
            "realistic full body studio identity card image of the same young girl, pure back view, "
            "no face visible, same age, same hair length and back-of-head shape, same body proportion, "
            f"full body visible including feet, plain white background, {PLACEHOLDER_OUTFIT}"
        ),
        width=512,
        height=768,
        face_weight=0.35,
        lora_strength=0.25,
    ),
}


def request_json(path: str, payload: dict | None = None, timeout: int = 30) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{SERVER}{path}", data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"ComfyUI is not reachable at {SERVER}. Start it first.") from exc


def assert_mps() -> None:
    stats = request_json("/system_stats", timeout=5)
    devices = stats.get("devices", [])
    if not any(device.get("type") == "mps" for device in devices):
        raise SystemExit("Refusing to run: ComfyUI is not using Apple MPS.")


def ensure_project_dirs() -> None:
    for dirname in [
        "00_输入参考",
        "01_头脸锁脸",
        "02_全身结构",
        "03_过程版本",
        "04_冻结母版",
        "05_最终交付",
    ]:
        (PROJECT_DIR / dirname).mkdir(parents=True, exist_ok=True)
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)


def check_references() -> None:
    missing = []
    for filename in REFERENCE_FILES.values():
        path = INPUT_DIR / filename
        if not path.exists() or path.stat().st_size == 0:
            missing.append(str(path))
    if missing:
        raise SystemExit("Missing reference image(s):\n" + "\n".join(missing))


def copy_references() -> None:
    ensure_project_dirs()
    for filename in REFERENCE_FILES.values():
        src = INPUT_DIR / filename
        dst = PROJECT_DIR / "00_输入参考" / filename
        if src.exists():
            shutil.copy2(src, dst)


def build_workflow(spec: ViewSpec, args: argparse.Namespace) -> dict:
    seed = args.seed if args.seed is not None else random.randint(1, 2**31 - 1)
    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": args.checkpoint},
        },
        "12": {
            "class_type": "LoadImage",
            "inputs": {"image": spec.face_ref},
        },
        "20": {
            "class_type": "IPAdapterUnifiedLoaderFaceID",
            "inputs": {
                "model": ["4", 0],
                "preset": "FACEID PLUS V2",
                "lora_strength": spec.lora_strength,
                "provider": "CPU",
            },
        },
        "21": {
            "class_type": "CLIPVisionLoader",
            "inputs": {"clip_name": args.clip_vision},
        },
        "22": {
            "class_type": "IPAdapterAdvanced",
            "inputs": {
                "model": ["20", 0],
                "ipadapter": ["20", 1],
                "image": ["12", 0],
                "weight": spec.face_weight,
                "weight_type": "linear",
                "combine_embeds": "average",
                "start_at": 0.0,
                "end_at": 0.88,
                "embeds_scaling": "V only",
                "clip_vision": ["21", 0],
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": spec.prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": args.negative, "clip": ["4", 1]},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": spec.width,
                "height": spec.height,
                "batch_size": 1,
            },
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": spec.steps,
                "cfg": spec.cfg,
                "sampler_name": args.sampler,
                "scheduler": args.scheduler,
                "denoise": 1.0,
                "model": ["22", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"nine_view/{spec.filename}_候选", "images": ["8", 0]},
        },
    }

    if spec.pose_ref:
        workflow["30"] = {"class_type": "LoadImage", "inputs": {"image": spec.pose_ref}}
        workflow["31"] = {
            "class_type": "OpenposePreprocessor",
            "inputs": {
                "image": ["30", 0],
                "detect_hand": "enable",
                "detect_body": "enable",
                "detect_face": "enable",
                "resolution": 512,
                "scale_stick_for_xinsr_cn": "disable",
            },
        }
        workflow["32"] = {
            "class_type": "ControlNetLoader",
            "inputs": {"control_net_name": args.controlnet},
        }
        workflow["33"] = {
            "class_type": "ControlNetApplyAdvanced",
            "inputs": {
                "positive": ["6", 0],
                "negative": ["7", 0],
                "control_net": ["32", 0],
                "image": ["31", 0],
                "strength": spec.pose_strength,
                "start_percent": 0.0,
                "end_percent": 0.82,
                "vae": ["4", 2],
            },
        }
        workflow["3"]["inputs"]["positive"] = ["33", 0]
        workflow["3"]["inputs"]["negative"] = ["33", 1]

    return workflow


def workflow_path(view: str) -> Path:
    spec = VIEWS[view]
    return WORKFLOW_DIR / f"{spec.code}_{spec.filename}.json"


def save_workflow(view: str, args: argparse.Namespace) -> Path:
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    path = workflow_path(view)
    path.write_text(
        json.dumps(build_workflow(VIEWS[view], args), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def queue_prompt(workflow: dict) -> str:
    return request_json("/prompt", {"prompt": workflow})["prompt_id"]


def wait_for(prompt_id: str, timeout: int) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = request_json(f"/history/{urllib.parse.quote(prompt_id)}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise SystemExit(f"Timed out waiting for prompt {prompt_id}")


def output_paths(history_item: dict) -> list[Path]:
    paths = []
    for output in history_item.get("outputs", {}).values():
        for image in output.get("images", []):
            if image.get("type") == "output":
                subfolder = image.get("subfolder") or ""
                paths.append(OUTPUT_DIR / subfolder / image["filename"])
    return paths


def run_view(view: str, args: argparse.Namespace) -> None:
    assert_mps()
    check_references()
    copy_references()
    path = save_workflow(view, args)
    prompt_id = queue_prompt(build_workflow(VIEWS[view], args))
    print(f"queued {view}: {prompt_id}")
    print(f"workflow: {path}")
    history_item = wait_for(prompt_id, args.timeout)
    outputs = output_paths(history_item)
    process_dir = PROJECT_DIR / "03_过程版本"
    process_dir.mkdir(parents=True, exist_ok=True)
    for src in outputs:
        if src.exists():
            dst = process_dir / f"{VIEWS[view].filename}_候选_{src.name}"
            shutil.copy2(src, dst)
            print(dst)


def freeze_view(view: str, src: Path) -> None:
    ensure_project_dirs()
    if not src.exists():
        raise SystemExit(f"Image does not exist: {src}")
    spec = VIEWS[view]
    frozen = PROJECT_DIR / "04_冻结母版" / f"{spec.filename}_冻结.png"
    final = PROJECT_DIR / "05_最终交付" / f"{spec.filename}.png"
    shutil.copy2(src, frozen)
    shutil.copy2(src, final)
    print(frozen)
    print(final)


def plan() -> None:
    for key in sorted(VIEWS):
        spec = VIEWS[key]
        pose = f", pose={spec.pose_ref}" if spec.pose_ref else ""
        print(f"{key} {spec.filename}: face={spec.face_ref}{pose}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="人物 9 视图 ComfyUI 标准执行器")
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--clip-vision", default=DEFAULT_CLIP_VISION)
    parser.add_argument("--controlnet", default=DEFAULT_CONTROLNET)
    parser.add_argument("--negative", default=NEGATIVE)
    parser.add_argument("--sampler", default="euler")
    parser.add_argument("--scheduler", default="normal")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--timeout", type=int, default=1800)

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="Create folders and copy input references")
    subparsers.add_parser("plan", help="Print the 9-view execution plan")

    build_parser = subparsers.add_parser("build", help="Build workflow JSON without running")
    build_parser.add_argument("--view", choices=sorted(VIEWS), required=True)
    subparsers.add_parser("build-all", help="Build all 9 workflow JSON files without running")

    run_parser = subparsers.add_parser("run", help="Run one view candidate")
    run_parser.add_argument("--view", choices=sorted(VIEWS), required=True)

    freeze_parser = subparsers.add_parser("freeze", help="Freeze one approved candidate")
    freeze_parser.add_argument("--view", choices=sorted(VIEWS), required=True)
    freeze_parser.add_argument("--src", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "init":
        check_references()
        copy_references()
        print(PROJECT_DIR)
        return
    if args.command == "plan":
        plan()
        return
    if args.command == "build":
        check_references()
        print(save_workflow(args.view, args))
        return
    if args.command == "build-all":
        check_references()
        for view in sorted(VIEWS):
            print(save_workflow(view, args))
        return
    if args.command == "run":
        run_view(args.view, args)
        return
    if args.command == "freeze":
        freeze_view(args.view, args.src)
        return


if __name__ == "__main__":
    main()
