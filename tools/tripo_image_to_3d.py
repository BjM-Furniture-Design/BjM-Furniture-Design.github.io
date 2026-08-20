# -*- coding: utf-8 -*-
"""Tripo image-to-3D. Output STL. Key: %USERPROFILE%\\.grok\\secrets\\tripo.env"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests
import trimesh

SECRET = Path.home() / ".grok" / "secrets" / "tripo.env"
BASE_V3 = "https://openapi.tripo3d.ai/v3"
BASE_V2 = "https://api.tripo3d.ai/v2/openapi"


def load_key() -> str:
    if not SECRET.exists():
        raise SystemExit(f"Missing {SECRET}")
    for line in SECRET.read_text(encoding="utf-8").splitlines():
        if line.startswith("TRIPO_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("TRIPO_API_KEY not found.")


def auth() -> dict:
    return {"Authorization": f"Bearer {load_key()}"}


def glb_to_stl(glb_path: Path, stl_path: Path) -> Path:
    loaded = trimesh.load(str(glb_path), force="mesh")
    if isinstance(loaded, trimesh.Scene):
        geoms = list(loaded.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if len(geoms) > 1 else geoms[0]
    else:
        mesh = loaded
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(str(stl_path))
    return stl_path


def generate_stl(image: Path, out_stl: Path, model: str = "v2.5-20250123") -> Path:
    H = auth()
    up = requests.post(
        f"{BASE_V3}/files",
        headers=H,
        files={"file": (image.name, image.read_bytes(), "image/jpeg")},
        timeout=120,
    )
    up.raise_for_status()
    token = up.json()["data"]["file_token"]
    ext = image.suffix.lstrip(".").lower()
    if ext == "jpeg":
        ext = "jpg"
    r = requests.post(
        f"{BASE_V3}/generation/image-to-model",
        headers={**H, "Content-Type": "application/json"},
        json={"file": {"type": ext, "file_token": token}, "model": model},
        timeout=60,
    )
    r.raise_for_status()
    task_id = r.json()["data"]["task_id"]
    data = None
    for _ in range(80):
        t = requests.get(f"{BASE_V3}/tasks/{task_id}", headers=H, timeout=30)
        t.raise_for_status()
        data = t.json()["data"]
        status = data.get("status")
        print("status", status, "progress", data.get("progress"))
        if status in ("success", "failed", "cancelled", "banned"):
            break
        time.sleep(3)
    if not data or data.get("status") != "success":
        raise SystemExit(f"task not success: {data}")
    url = (data.get("output") or {}).get("model_url")
    if not url:
        raise SystemExit("no model_url")
    glb = out_stl.with_suffix(".glb")
    glb.write_bytes(requests.get(url, timeout=180).content)
    return glb_to_stl(glb, out_stl)


if __name__ == "__main__":
    H = auth()
    b = requests.get(f"{BASE_V2}/user/balance", headers=H, timeout=20)
    print("balance", b.text)
    if len(sys.argv) < 3:
        print("Usage: python tripo_image_to_3d.py <image> <out.stl>")
        sys.exit(0)
    path = generate_stl(Path(sys.argv[1]), Path(sys.argv[2]))
    print("STL", path, path.stat().st_size)
