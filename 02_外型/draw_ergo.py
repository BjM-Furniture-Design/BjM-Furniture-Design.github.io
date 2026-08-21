# -*- coding: utf-8 -*-
"""人體尺度圖 — 室內設計資料集式黑白線圖（WAVE / KOALA / F180 原創，不複製原書圖）。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Polygon, Rectangle
from matplotlib.font_manager import FontProperties
from PIL import Image
import numpy as np

from draw_cad_3view import (
    catmull, fill_curve, side_outer, side_void, side_cushion,
    front_outer, top_outer, D, H, W, SH_PAD, ARM_H, SEAT_D, SEAT_W, VOID_H,
)

OUT = Path(__file__).resolve().parent
FONT = FontProperties(fname=r"C:\Windows\Fonts\msjh.ttc")
FONTB = FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc")

INK = "#111111"
GRAY = "#5A5A5A"
FILL = "#3C3C3C"
PAPER = "#FFFEFB"
DPI = 170
PIMP_DIR = OUT / "_pimp"
# Free PNG scale figures from pimpmydrawing.com (do not redistribute SVG).
PIMP = {
    "sit_lounge": "young-man-sitting-chilling-and-looking-at-the-side-as-a-cad-block-2d-people-109-pimpmydrawing.png",
    "stand_side": "man-standing-dwg-cad-132-pimpmydrawing.png",
    "stand_walk": "man-walking-dwg-cad-130-pimpmydrawing.png",
    "stand_woman": "woman-standing-dwg-cad-134-pimpmydrawing.png",
    "child": "a-boy-standing-looking-in-the-camera-cad-people-77-pimpmydrawing.png",
    "girl": "girl-with-shorts-standing-looking-in-the-camera-people-dwg-52-pimpmydrawing.png",
    "sit_chair": "man-sitting-people-dwg-185-pimpmydrawing.png",
    "top": "person-standing-top-view-vector-persons-pimpmydrawing-6359.png",
}
_FIG_CACHE = {}


def load_pimp(key):
    if key in _FIG_CACHE:
        return _FIG_CACHE[key]
    path = PIMP_DIR / PIMP[key]
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    rgb, al = a[:, :, :3].astype(np.float32), a[:, :, 3]
    mask = al > 12
    if mask.any() and rgb[mask].mean() > 160:
        rgb = 255 - rgb
        a[:, :, :3] = rgb.astype(np.uint8)
    ys, xs = np.where(al > 12)
    a = a[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
    _FIG_CACHE[key] = a
    return a


def place_pimp(ax, key, x, y, h_plate, flip=False, center=False, z=8):
    """Place a pimpmydrawing figure. (x,y) = left-bottom, or center-bottom if center."""
    arr = load_pimp(key)
    if flip:
        arr = arr[:, ::-1].copy()
    ph, pw = arr.shape[:2]
    w_plate = pw / ph * h_plate
    x0 = x - w_plate / 2 if center else x
    ax.imshow(arr, extent=[x0, x0 + w_plate, y, y + h_plate],
              origin="upper", interpolation="bilinear", zorder=z, aspect="auto")
    return w_plate


def save(fig, path):
    fig.savefig(path, dpi=DPI, facecolor=PAPER, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("wrote", path, path.stat().st_size)


def new_plate(w=16.2, h=10.4):
    fig, ax = plt.subplots(figsize=(w, h), dpi=DPI, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def frame(ax, x0, y0, x1, y1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=INK, lw=1.0, zorder=30))


def plate_title(ax, x, y, num, title):
    ax.add_patch(Rectangle((x, y - 7), 16, 16, facecolor=INK, edgecolor="none", zorder=31))
    ax.text(x + 8, y + 1, str(num), color="#fff", ha="center", va="center",
            fontproperties=FONTB, fontsize=11, zorder=32)
    ax.text(x + 22, y + 1, title, color=INK, ha="left", va="center",
            fontproperties=FONTB, fontsize=12, zorder=32)


def caption(ax, x, y, text, ha="center"):
    ax.text(x, y, text, ha=ha, va="top", fontproperties=FONT, fontsize=8, color=INK)


def dim_h(ax, x1, x2, y, text, dy=18, fs=7.5):
    lo, hi = min(x1, x2), max(x1, x2)
    ax.plot([x1, x1], [y, y + dy], color=INK, lw=0.4, zorder=12)
    ax.plot([x2, x2], [y, y + dy], color=INK, lw=0.4, zorder=12)
    yy = y + dy
    ax.annotate("", xy=(hi, yy), xytext=(lo, yy),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.55, mutation_scale=7), zorder=12)
    ax.text((x1 + x2) / 2, yy + 3.2, text, ha="center", va="bottom",
            fontproperties=FONT, fontsize=fs, color=INK, zorder=13)


def dim_h_below(ax, x1, x2, y, text, dy=18, fs=7.5):
    ax.plot([x1, x1], [y, y - dy], color=INK, lw=0.4, zorder=12)
    ax.plot([x2, x2], [y, y - dy], color=INK, lw=0.4, zorder=12)
    yy = y - dy
    lo, hi = min(x1, x2), max(x1, x2)
    ax.annotate("", xy=(hi, yy), xytext=(lo, yy),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.55, mutation_scale=7), zorder=12)
    ax.text((x1 + x2) / 2, yy - 3.0, text, ha="center", va="top",
            fontproperties=FONT, fontsize=fs, color=INK, zorder=13)


def dim_v(ax, y1, y2, x, text, dx=16, fs=7.5, left=True):
    ax.plot([x, x + (-dx if left else dx)], [y1, y1], color=INK, lw=0.4, zorder=12)
    ax.plot([x, x + (-dx if left else dx)], [y2, y2], color=INK, lw=0.4, zorder=12)
    xx = x + (-dx if left else dx)
    lo, hi = min(y1, y2), max(y1, y2)
    ax.annotate("", xy=(xx, hi), xytext=(xx, lo),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.55, mutation_scale=7), zorder=12)
    ax.text(xx + (-3.2 if left else 3.2), (y1 + y2) / 2, text,
            ha="right" if left else "left", va="center", rotation=90,
            fontproperties=FONT, fontsize=fs, color=INK, zorder=13)


def label(ax, x, y, text, fs=7, color=INK, ha="left", va="bottom", rot=0):
    ax.text(x, y, text, ha=ha, va=va, rotation=rot, fontproperties=FONT,
            fontsize=fs, color=color, zorder=13)


def gl(ax, x0, x1, y):
    ax.plot([x0, x1], [y, y], color=INK, lw=0.9, zorder=4)


# ---------------------------------------------------------------------------
# Anthropometric figures (mm in local space, then placed)
# ---------------------------------------------------------------------------
def line(ax, pts, lw=0.85, ls="-", z=8):
    a = np.asarray(pts, float)
    ax.plot(a[:, 0], a[:, 1], color=INK, lw=lw, ls=ls, zorder=z,
            solid_capstyle="round", solid_joinstyle="round")


def stroke_sit(ax, hipx, hipy, s, face=1, lounge=True):
    """Textbook side-seated figure: hip at (hipx,hipy), face +1 = +x."""
    f = face

    def P(x, z):
        return (hipx + f * x * s, hipy + z * s)

    if lounge:
        hx, hz, hr_x, hr_z = 100, 305, 36, 44
        back = [P(12, 8), P(40, 120), P(70, 230), P(88, 270)]
        chest = [P(22, 12), P(58, 125), P(92, 235)]
        thigh = [P(8, 6), P(180, 16), P(360, 8)]
        shin = [P(360, 8), P(385, -150), P(400, -350)]
        foot = [P(400, -350), P(455, -372), P(510, -378)]
        arm = [P(78, 240), P(190, 150), P(320, 55)]
        eye_z = 305
    else:
        hx, hz, hr_x, hr_z = 18, 355, 34, 42
        back = [P(0, 8), P(4, 140), P(8, 250), P(10, 295)]
        chest = [P(22, 10), P(28, 150), P(32, 255)]
        thigh = [P(8, 6), P(190, 10), P(380, 4)]
        shin = [P(380, 4), P(392, -160), P(400, -355)]
        foot = [P(400, -355), P(460, -375), P(515, -380)]
        arm = [P(28, 250), P(160, 175), P(300, 85)]
        eye_z = 355
    ax.add_patch(Ellipse(P(hx, hz), hr_x * 2 * s, hr_z * 2 * s,
                         fill=False, ec=INK, lw=0.9, zorder=9))
    line(ax, back, lw=0.9)
    line(ax, chest, lw=0.7)
    line(ax, thigh, lw=0.9)
    line(ax, shin, lw=0.9)
    line(ax, foot, lw=0.9)
    line(ax, arm, lw=0.8)
    return P(hx, hz)[1]  # eye height on plate


def fill_stand(ax, heelx, heely, s, face=1, h=1750):
    """Filled standing SIDE figure. heelx = heel, height h mm, chest ~240 mm deep."""
    k = h / 1750.0
    f = face

    def P(x, z):
        return (heelx + f * x * s, heely + z * k * s)

    ax.add_patch(Ellipse(P(110, 1640), 150 * s * k, 200 * s * k,
                         facecolor=FILL, edgecolor=INK, lw=0.35, zorder=7))
    body = np.array([
        P(50, 1545), P(30, 1360), P(40, 1080), P(55, 900),
        P(50, 520), P(40, 90), P(15, 20), P(40, 0),
        P(230, 0), P(255, 18), P(200, 42), P(95, 90),
        P(90, 520), P(100, 900), P(210, 1120), P(220, 1360), P(175, 1545),
    ])
    ax.add_patch(Polygon(body, closed=True, facecolor=FILL, edgecolor=INK,
                         lw=0.35, zorder=6))
    arm = np.array([P(220, 1360), P(250, 1120), P(240, 980), P(215, 970),
                    P(220, 1110), P(195, 1335)])
    ax.add_patch(Polygon(arm, closed=True, facecolor=FILL, edgecolor=INK,
                         lw=0.3, zorder=7))


def fill_stand_front(ax, cx, heely, s, h=1750):
    """Filled standing FRONT figure, centered on cx. Shoulder ~420 mm."""
    k = h / 1750.0

    def P(x, z):
        return (cx + x * s, heely + z * k * s)

    ax.add_patch(Ellipse(P(0, 1640), 170 * s * k, 200 * s * k,
                         facecolor=FILL, edgecolor=INK, lw=0.35, zorder=7))
    body = np.array([
        P(-40, 1540), P(-200, 1470), P(-185, 1180), P(-90, 980),
        P(-75, 500), P(-60, 50), P(-115, 0), P(-15, 0), P(-25, 45),
        P(-20, 490),
        P(20, 490), P(25, 45), P(15, 0), P(115, 0), P(60, 50),
        P(75, 500), P(90, 980), P(185, 1180), P(200, 1470), P(40, 1540),
    ])
    ax.add_patch(Polygon(body, closed=True, facecolor=FILL, edgecolor=INK,
                         lw=0.35, zorder=6))


def plan_person(ax, cx, cy, s, heading_deg=0):
    """Top-view sitter, heading is face direction in degrees (0=+x)."""
    ang = np.deg2rad(heading_deg)
    c, sn = np.cos(ang), np.sin(ang)

    def R(x, y):
        return (cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s)

    # head
    hx, hy = R(0, 0)
    ax.add_patch(Circle((hx, hy), 48 * s, fill=False, ec=INK, lw=0.85, zorder=8))
    # shoulders / upper body
    body = [R(-70, 40), R(-95, 90), R(-80, 200), R(-30, 250),
            R(30, 250), R(80, 200), R(95, 90), R(70, 40)]
    line(ax, body + [body[0]], lw=0.8)
    # arms on furniture
    line(ax, [R(-95, 90), R(-140, 70), R(-160, 40)], lw=0.7)
    line(ax, [R(95, 90), R(140, 70), R(160, 40)], lw=0.7)


# ---------------------------------------------------------------------------
# WAVE
# ---------------------------------------------------------------------------
def draw_wave():
    fig, ax = new_plate(16.6, 11.0)
    frame(ax, 0, 0, 430, 280)
    plate_title(ax, 8, 263, 3, "WAVE-LC-001　休閒椅常用人體尺寸")
    label(ax, 422, 264, "單位 mm", fs=7.5, ha="right", va="center", color=GRAY)

    so, sv, sc = side_outer(), side_void(), side_cushion()
    fo, to = front_outer(), top_outer()

    def chair_side(ox, oy, s, lw=1.0):
        ax.plot(ox + so[:, 0] * s, oy + so[:, 1] * s, color=INK, lw=lw, zorder=5)
        ax.plot(ox + sv[:, 0] * s, oy + sv[:, 1] * s, color=INK, lw=0.5, zorder=5)
        ax.plot(ox + sc[:, 0] * s, oy + sc[:, 1] * s, color=INK, lw=0.5,
                ls=(0, (2.2, 1.4)), zorder=5)
        gl(ax, ox - 6, ox + D * s + 8, oy)

    # A 躺坐側視  — front is +x (right)
    S = 0.078
    ox, oy = 58, 155
    chair_side(ox, oy, S, 1.1)
    place_pimp(ax, "sit_lounge", ox + 175 * S, oy + 6 * S, 700 * S, flip=False)
    eye_y = oy + 705 * S
    ax.plot([ox + 180 * S, ox + 980 * S], [eye_y, eye_y],
            color=INK, lw=0.45, ls=(0, (3, 2)), zorder=9)
    label(ax, ox + 988 * S, eye_y, "視線", fs=7.2, va="center")
    dim_v(ax, oy, oy + H * S, ox - 4, "820", dx=13)
    dim_v(ax, oy, oy + ARM_H * S, ox - 4, "580", dx=26)
    dim_v(ax, oy, oy + SH_PAD * S, ox - 4, "400", dx=39)
    dim_h_below(ax, ox, ox + D * S, oy, "960", dy=13)
    dim_h(ax, ox + 310 * S, ox + 830 * S, oy + 448 * S, "520", dy=11)
    label(ax, ox + 700 * S, oy + 640 * S, "20°", fs=7.5, color=GRAY)
    label(ax, ox + 250 * S, oy + 348 * S, "5°", fs=7.5, color=GRAY)
    caption(ax, ox + D * S * 0.5, oy - 32, "躺坐側視（肩背支撐，非頭枕）")

    # B 椅後通行
    S2 = 0.062
    bx, by = 52, 28
    chair_side(bx, by, S2, 0.95)
    place_pimp(ax, "sit_lounge", bx + 150 * S2, by + 5 * S2, 680 * S2)
    place_pimp(ax, "stand_walk", bx + D * S2 + 38, by, 1750 * S2)
    dim_h(ax, bx + D * S2, bx + D * S2 + 70, by + 80 * S2, "600~800", dy=16)
    label(ax, bx + D * S2 + 35, by + 200 * S2, "通行區", fs=7, ha="center")
    dim_v(ax, by, by + 400 * S2, bx + 420 * S2, "400", dx=11, left=False, fs=7)
    caption(ax, bx + 70, by - 30, "椅後通行／起身")

    # C 平面
    sp = 0.058
    px, py = 300, 168
    ax.plot(px + to[:, 0] * sp, py + to[:, 1] * sp, color=INK, lw=1.0, zorder=5)
    ax.plot([px, px], [py + 40 * sp, py + 920 * sp], color=GRAY, lw=0.35, ls=(0, (2, 1.6)))
    plan_person(ax, px, py + 500 * sp, sp, heading_deg=-90)
    dim_h(ax, px - 450 * sp, px + 450 * sp, py + 970 * sp, "900", dy=11)
    dim_v(ax, py, py + 960 * sp, px + 460 * sp, "960", dx=13, left=False)
    dim_h_below(ax, px - 270 * sp, px + 270 * sp, py + 220 * sp, "540", dy=11)
    caption(ax, px, py - 28, "平面　座盆內寬 540")

    # D 正視
    sf = 0.058
    fx0, fy = 318, 28
    ax.plot(fx0 + fo[:, 0] * sf, fy + fo[:, 1] * sf, color=INK, lw=1.0, zorder=5)
    gl(ax, fx0 - 78, fx0 + 95, fy)
    place_pimp(ax, "stand_woman", fx0 - 95, fy, 1650 * sf)
    place_pimp(ax, "stand_walk", fx0 + 58, fy, 1750 * sf)
    dim_h(ax, fx0 - 450 * sf, fx0 + 450 * sf, fy + 830 * sf, "900", dy=10)
    dim_h_below(ax, fx0 - 62, fx0 - 450 * sf, fy, "450~610", dy=12)
    label(ax, fx0 - 62, fy + 90 * sf, "通行", fs=7, ha="center")
    caption(ax, fx0, fy - 30, "正視　兩側通行淨寬")

    ax.plot([8, 422], [11, 11], color=INK, lw=0.3)
    label(ax, 10, 5,
          "座高含墊 400    有效座深 520    座盆內寬 540    扶手 580    總高 820    總深 960    靠背 20°    座面 5°    人物 pimpmydrawing.com",
          fs=7, va="center", color=GRAY)

    ax.set_xlim(-2, 432)
    ax.set_ylim(-2, 282)
    save(fig, OUT / "WAVE-LC-001_ergo.png")


# ---------------------------------------------------------------------------
# KOALA
# ---------------------------------------------------------------------------
def draw_koala():
    fig, ax = new_plate(16.4, 10.4)
    S = 0.048
    frame(ax, 0, 0, 420, 265)
    plate_title(ax, 8, 249, 3, "KOALA-CR-001　衣帽架常用人體尺寸")
    label(ax, 412, 250, "單位 mm", fs=7.5, ha="right", va="center", color=GRAY)

    # ---- A. side reach ----
    ox, oy = 70, 28
    Htot = 1280
    # base + posts + pegs
    for z, rx in [(6, 90), (16, 86), (26, 82)]:
        ax.add_patch(Ellipse((ox, oy + z * S), rx * 2 * S, 12 * S,
                             fill=False, ec=INK, lw=0.7, zorder=5))
    ax.plot([ox - 6 * S, ox - 6 * S], [oy + 28 * S, oy + Htot * S], color=INK, lw=1.2)
    ax.plot([ox + 6 * S, ox + 6 * S], [oy + 28 * S, oy + Htot * S], color=INK, lw=1.2)
    for z in (770, 965, 1170):
        ax.plot([ox + 8 * S, ox + 110 * S], [oy + z * S, oy + (z + 40) * S], color=INK, lw=1.4,
                solid_capstyle="round")
        ax.plot([ox - 8 * S, ox - 110 * S], [oy + (z + 6) * S, oy + (z + 46) * S], color=INK, lw=1.4,
                solid_capstyle="round")
        ax.add_patch(Circle((ox + 110 * S, oy + (z + 40) * S), 3.2, fill=False, ec=INK, lw=0.6))
        ax.add_patch(Circle((ox - 110 * S, oy + (z + 46) * S), 3.2, fill=False, ec=INK, lw=0.6))
    gl(ax, ox - 40, ox + 220, oy)

    dim_v(ax, oy, oy + Htot * S, ox - 130 * S, "1280", dx=14)
    for z, t in ((770, "770"), (965, "965"), (1170, "1170")):
        ax.plot([ox + 120 * S, ox + 175 * S], [oy + z * S, oy + z * S],
                color=INK, lw=0.4, ls=(0, (2, 1.4)))
        label(ax, ox + 180 * S, oy + z * S, t, fs=7.5, va="center")

    # overcoat dashed
    ax.plot([ox - 40, ox + 210], [oy + 1650 * S, oy + 1650 * S],
            color=GRAY, lw=0.5, ls=(0, (3, 2)))
    label(ax, ox - 38, oy + 1660 * S, "1650 大衣掛點（本 SKU 不到）", fs=7, color=GRAY)

    caption(ax, ox + 20, oy - 16, "側視：三層掛點")

    # ---- B. adult + child ----
    ax2x, ay = 175, 28
    place_pimp(ax, "stand_woman", ax2x, ay, 1650 * S)
    place_pimp(ax, "child", ax2x + 55, ay, 1200 * S)
    gl(ax, ax2x - 15, ax2x + 90, ay)
    dim_v(ax, ay, ay + 1750 * S, ax2x - 8, "1750", dx=12)
    dim_v(ax, ay, ay + 1200 * S, ax2x + 78, "1200", dx=12, left=False)
    # reach dashed from child to lower pegs conceptually
    ax.plot([ax2x + 18, ax2x + 18], [ay, ay + 1200 * S], color=GRAY, lw=0.3, ls=(0, (2, 1.5)))
    caption(ax, ax2x + 35, ay - 16, "成人 1750／兒童 1200")

    # ---- C. plan ----
    px, py = 300, 155
    sp = 0.12
    ax.add_patch(Circle((px, py), 90 * sp, fill=False, ec=INK, lw=0.9))
    ax.add_patch(Circle((px, py), 12 * sp, fill=False, ec=INK, lw=0.7))
    # peg sweep
    ax.add_patch(Circle((px, py), 120 * sp, fill=False, ec=GRAY, lw=0.45, ls=(0, (2, 1.5))))
    # standing ring
    ax.add_patch(Circle((px, py), 400 * sp, fill=False, ec=INK, lw=0.45, ls=(0, (3, 2))))
    plan_person(ax, px + 280 * sp, py, sp * 0.9, heading_deg=0)
    dim_h(ax, px - 90 * sp, px + 90 * sp, py + 90 * sp, "Ø180", dy=10)
    dim_h_below(ax, px - 400 * sp, px + 400 * sp, py - 400 * sp, "活動半徑 約 800", dy=12)
    caption(ax, px, py - 400 * sp - 28, "平面：花座 Ø180，偏小須配重或牆扣")

    ax.plot([8, 412], [10, 10], color=INK, lw=0.3)
    label(ax, 10, 5, "兒童房／玄關短掛　·　不是大廳大衣架　·　人物 pimpmydrawing.com",
          fs=7, va="center", color=GRAY)

    ax.set_xlim(-2, 422)
    ax.set_ylim(-2, 268)
    save(fig, OUT / "無尾熊-衣帽架" / "KOALA-CR-001_ergo.png")


# ---------------------------------------------------------------------------
# F180
# ---------------------------------------------------------------------------
def draw_f180():
    fig, ax = new_plate(16.4, 10.4)
    S = 0.052
    frame(ax, 0, 0, 420, 265)
    plate_title(ax, 8, 249, 3, "F180-RC-001　旋轉繪圖櫃常用人體尺寸")
    label(ax, 412, 250, "單位 mm", fs=7.5, ha="right", va="center", color=GRAY)

    # ---- A. side / front elevation of tower ----
    ox, oy = 55, 30
    w, h = 560, 1150
    ax.add_patch(Rectangle((ox, oy), w * S, h * S, fill=False, ec=INK, lw=1.05, zorder=5))
    for z in (0, 405, 810, 1150 - 18):
        ax.plot([ox, ox + w * S], [oy + z * S, oy + z * S], color=INK, lw=0.7, zorder=5)
    # bins
    for bz, bh in ((24, 170), (430, 170)):
        ax.add_patch(Rectangle((ox + 40 * S, oy + bz * S), 200 * S, bh * S,
                               fill=False, ec=INK, lw=0.5))
        ax.add_patch(Rectangle((ox + 310 * S, oy + bz * S), 200 * S, bh * S,
                               fill=False, ec=INK, lw=0.5))
    gl(ax, ox - 10, ox + w * S + 120, oy)
    dim_v(ax, oy, oy + h * S, ox - 4, "1150", dx=14)
    dim_h_below(ax, ox, ox + w * S, oy, "560", dy=12)
    label(ax, ox + w * S + 6, oy + 1030 * S, "220", fs=7.5, va="center")
    label(ax, ox + w * S + 6, oy + 610 * S, "405", fs=7.5, va="center")
    label(ax, ox + w * S + 6, oy + 200 * S, "405", fs=7.5, va="center")
    ax.plot([ox + w * S, ox + w * S + 14], [oy + 1030 * S, oy + 1030 * S], color=INK, lw=0.35)
    ax.plot([ox + w * S, ox + w * S + 14], [oy + 610 * S, oy + 610 * S], color=INK, lw=0.35)
    ax.plot([ox + w * S, ox + w * S + 14], [oy + 200 * S, oy + 200 * S], color=INK, lw=0.35)

    place_pimp(ax, "stand_side", ox + w * S + 18, oy, 1750 * S)
    place_pimp(ax, "child", ox + w * S + 72, oy, 1200 * S)
    dim_v(ax, oy, oy + 1750 * S, ox + w * S + 118, "1750", dx=12, left=False)
    caption(ax, ox + w * S / 2, oy - 28, "立面：站著擺物，不是書桌")

    # sight / reach
    ax.plot([ox + w * S + 8, ox + w * S + 70], [oy + 1150 * S, oy + 1600 * S],
            color=INK, lw=0.4, ls=(0, (2, 1.6)))
    label(ax, ox + w * S + 72, oy + 1610 * S, "視線／取物", fs=7)

    # ---- B. plan + rotation ----
    px, py = 250, 155
    sp = 0.07
    ax.add_patch(mpatches.FancyBboxPatch((px - 280 * sp, py - 280 * sp), 560 * sp, 560 * sp,
                                         boxstyle="round,pad=0,rounding_size=1.26",
                                         fill=False, ec=INK, lw=1.0))
    ax.add_patch(Circle((px, py), 280 * sp * np.sqrt(2), fill=False, ec=GRAY, lw=0.45,
                        ls=(0, (3, 2))))
    plan_person(ax, px + 420 * sp, py, sp, heading_deg=0)
    dim_h(ax, px - 280 * sp, px + 280 * sp, py + 280 * sp, "560", dy=10)
    dim_v(ax, py - 280 * sp, py + 280 * sp, px + 280 * sp, "560", dx=12, left=False)
    label(ax, px + 8, py + 280 * sp * np.sqrt(2) + 4, "旋轉外接圓", fs=7, color=GRAY)
    caption(ax, px, py - 280 * sp - 26, "平面：旋轉淨空，抽板前先鎖")

    # ---- C. bay notes ----
    tx, ty = 318, 28
    for i, t in enumerate(["上層 220  小箱／畫具，兒童踮腳",
                           "中層 405  A3 板或兩箱",
                           "下層 405  A3 板或兩箱",
                           "內淨寬 284  外購箱必須對口",
                           "抽板 297  先鎖旋轉",
                           "層縫 小於 5 或 大於 12  防夾"]):
        label(ax, tx, ty + 88 - i * 14, t, fs=7.2, va="center")
    caption(ax, tx + 40, ty - 14, "層高與使用")

    ax.plot([8, 412], [10, 10], color=INK, lw=0.3)
    label(ax, 10, 5, "總高 1150 適合作畫／擺物　·　軸承必須能鎖　·　不是成人書桌　·　人物 pimpmydrawing.com",
          fs=7, va="center", color=GRAY)

    ax.set_xlim(-2, 422)
    ax.set_ylim(-2, 268)
    save(fig, OUT / "旋轉繪圖櫃" / "F180-RC-001_ergo.png")


if __name__ == "__main__":
    draw_wave()
    draw_koala()
    draw_f180()
