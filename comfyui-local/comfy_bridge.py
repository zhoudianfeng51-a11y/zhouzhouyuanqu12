#!/usr/bin/env python3
"""
Small local bridge for talking to the user's ComfyUI instance.

No third-party Python packages are required. It can check the local server,
list available checkpoints, submit a basic txt2img workflow, and wait for output.
"""

from __future__ import annotations

import argparse
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SERVER = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("/Users/a1234/Documents/comfy/ComfyUI/output")
DEFAULT_CHECKPOINT = "v1-5-pruned-emaonly.safetensors"


def request_json(path: str, payload: dict | None = None) -> dict:
    url = f"{SERVER}{path}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"Cannot reach ComfyUI at {SERVER}: {exc}") from exc


def status(_: argparse.Namespace) -> None:
    stats = request_json("/system_stats")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def checkpoints(_: argparse.Namespace) -> None:
    info = request_json("/object_info/CheckpointLoaderSimple")
    ckpts = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    for ckpt in ckpts:
        print(ckpt)


def build_txt2img_workflow(args: argparse.Namespace) -> dict:
    seed = args.seed if args.seed is not None else random.randint(1, 2**31 - 1)
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": args.steps,
                "cfg": args.cfg,
                "sampler_name": args.sampler,
                "scheduler": args.scheduler,
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": args.checkpoint},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": args.width,
                "height": args.height,
                "batch_size": args.batch_size,
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": args.prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": args.negative, "clip": ["4", 1]},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": args.prefix, "images": ["8", 0]},
        },
    }


def queue_prompt(workflow: dict) -> str:
    response = request_json("/prompt", {"prompt": workflow})
    return response["prompt_id"]


def wait_for_prompt(prompt_id: str, timeout: int) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = request_json(f"/history/{urllib.parse.quote(prompt_id)}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise SystemExit(f"Timed out waiting for prompt {prompt_id}")


def output_paths(history_item: dict) -> list[Path]:
    paths: list[Path] = []
    for node in history_item.get("outputs", {}).values():
        for image in node.get("images", []):
            if image.get("type") == "output":
                paths.append(OUTPUT_DIR / image["filename"])
    return paths


def txt2img(args: argparse.Namespace) -> None:
    workflow = build_txt2img_workflow(args)
    if args.save_workflow:
        Path(args.save_workflow).write_text(
            json.dumps(workflow, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    prompt_id = queue_prompt(workflow)
    print(f"queued: {prompt_id}")
    history_item = wait_for_prompt(prompt_id, args.timeout)
    paths = output_paths(history_item)
    if not paths:
        print(json.dumps(history_item, ensure_ascii=False, indent=2))
        raise SystemExit("Prompt finished, but no output image was reported.")
    for path in paths:
        print(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local ComfyUI bridge")
    subparsers = parser.add_subparsers(required=True)

    status_parser = subparsers.add_parser("status", help="Check ComfyUI status")
    status_parser.set_defaults(func=status)

    ckpt_parser = subparsers.add_parser("checkpoints", help="List checkpoints")
    ckpt_parser.set_defaults(func=checkpoints)

    txt_parser = subparsers.add_parser("txt2img", help="Submit a basic txt2img job")
    txt_parser.add_argument("--prompt", required=True)
    txt_parser.add_argument(
        "--negative",
        default="low quality, blurry, distorted, watermark, text, extra fingers",
    )
    txt_parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    txt_parser.add_argument("--width", type=int, default=512)
    txt_parser.add_argument("--height", type=int, default=512)
    txt_parser.add_argument("--batch-size", type=int, default=1)
    txt_parser.add_argument("--steps", type=int, default=20)
    txt_parser.add_argument("--cfg", type=float, default=7.0)
    txt_parser.add_argument("--sampler", default="euler")
    txt_parser.add_argument("--scheduler", default="normal")
    txt_parser.add_argument("--seed", type=int)
    txt_parser.add_argument("--prefix", default="codex_txt2img")
    txt_parser.add_argument("--timeout", type=int, default=600)
    txt_parser.add_argument("--save-workflow")
    txt_parser.set_defaults(func=txt2img)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
