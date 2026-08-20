# -*- coding: utf-8 -*-
"""Pack a textured GLB as Apple Quick Look USDZ (keep baseColor)."""
from __future__ import annotations

import io
import struct
import zipfile
from pathlib import Path

import trimesh


def _align_extra(offset: int, namelen: int, alignment: int = 64) -> bytes:
    # local header is 30 + namelen + extra; data should start at multiple of 64
    header = 30 + namelen
    start = offset + header
    pad = (alignment - (start % alignment)) % alignment
    return b"\x00" * pad


def write_usdz(out: Path, entries: list[tuple[str, bytes]]) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        offset = 0
        for name, data in entries:
            extra = _align_extra(offset, len(name.encode("utf-8")))
            info = zipfile.ZipInfo(filename=name)
            info.compress_type = zipfile.ZIP_STORED
            info.extra = extra
            zf.writestr(info, data)
            # 30 + name + extra + data + 16 data descriptor? ZipFile may not match.
            offset = buf.tell()
    out.write_bytes(buf.getvalue())


def glb_to_usdz(glb: Path, usdz: Path) -> Path:
    scene = trimesh.load(str(glb))
    mesh = list(scene.geometry.values())[0] if isinstance(scene, trimesh.Scene) else scene
    vis = mesh.visual
    uv = vis.uv
    img = vis.material.baseColorTexture
    tex_bytes = io.BytesIO()
    img.convert("RGB").save(tex_bytes, format="JPEG", quality=85)
    tex = tex_bytes.getvalue()

    pts = mesh.vertices
    faces = mesh.faces
    mn, mx = pts.min(0), pts.max(0)

    def f3(a):
        return ", ".join(f"({x:.6f}, {y:.6f}, {z:.6f})" for x, y, z in a)

    def ijoin(a):
        return ", ".join(str(int(i)) for i in a)

    def uvjoin(a):
        return ", ".join(f"({u:.6f}, {1.0 - v:.6f})" for u, v in a)

    counts = ", ".join("3" for _ in range(len(faces)))
    indices = ", ".join(str(int(i)) for tri in faces for i in tri)

    usda = f"""#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Chair" (
    kind = "component"
)
{{
    def Mesh "mesh"
    {{
        float3[] extent = [({mn[0]:.6f}, {mn[1]:.6f}, {mn[2]:.6f}), ({mx[0]:.6f}, {mx[1]:.6f}, {mx[2]:.6f})]
        int[] faceVertexCounts = [{counts}]
        int[] faceVertexIndices = [{indices}]
        rel material:binding = </Chair/mat>
        point3f[] points = [{f3(pts)}]
        texCoord2f[] primvars:st = [{uvjoin(uv)}] (
            interpolation = "vertex"
        )
        uniform token subdivisionScheme = "none"
    }}

    def Material "mat"
    {{
        token outputs:surface.connect = </Chair/mat/preview.outputs:surface>

        def Shader "preview"
        {{
            uniform token info:id = "UsdPreviewSurface"
            color3f inputs:diffuseColor.connect = </Chair/mat/tex.outputs:rgb>
            float inputs:metallic = 0
            float inputs:roughness = 0.6
            token outputs:surface
        }}

        def Shader "st"
        {{
            uniform token info:id = "UsdPrimvarReader_float2"
            token inputs:varname = "st"
            float2 outputs:result
        }}

        def Shader "tex"
        {{
            uniform token info:id = "UsdUVTexture"
            asset inputs:file = @tex.jpg@
            float2 inputs:st.connect = </Chair/mat/st.outputs:result>
            token inputs:wrapS = "repeat"
            token inputs:wrapT = "repeat"
            float3 outputs:rgb
        }}
    }}
}}
"""
    write_usdz(usdz, [("model.usda", usda.encode("utf-8")), ("tex.jpg", tex)])
    return usdz


if __name__ == "__main__":
    import sys
    glb_to_usdz(Path(sys.argv[1]), Path(sys.argv[2]))
    print("ok", sys.argv[2])
