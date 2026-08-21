# -*- coding: utf-8 -*-
"""Professional ergonomic elevations for WAVE / KOALA / F180 (web, retina PNG)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, PathPatch, Arc
from matplotlib.path import Path as MPath
import numpy as np

from draw_cad_3view import (
    FONT, FONTB, WOOD, WOOD_EDGE, CUSH, CUSH_EDGE, INK, THIN,
    ACCENT, PAPER, fill_curve, side_outer, side_void, side_cushion,
    side_pocket_lip, D, H, SH_PAD, ARM_H, SEAT_D, VOID_H, SH_WOOD,
)

OUT = Path(__file__).resolve().parent
FIG = "#2A241C"
FIG_A = 0.92
DPI = 180


def capsule(ax, p1, p2, r, fc=FIG, ec="none", alpha=FIG_A, z=6):
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    d = p2 - p1
    L = float(np.linalg.norm(d))
    kw = dict(facecolor=fc, edgecolor=ec, lw=0, alpha=alpha, zorder=z, joinstyle="round")
    if L < 0.8:
        ax.add_patch(Circle(p1, r, **kw))
        return
    u = d / L
    n = np.array([-u[1], u[0]])
    poly = [p1 + n * r, p1 - n * r, p2 - n * r, p2 + n * r]
    ax.add_patch(Polygon(poly, closed=True, **kw))
    ax.add_patch(Circle(p1, r, **kw))
    ax.add_patch(Circle(p2, r, **kw))


def dim_v_left(ax, z1, z2, x, text, dx=70, fs=9.5):
    lo, hi = min(z1, z2), max(z1, z2)
    xx = x - dx
    ax.plot([x, xx - 8], [z1, z1], color=INK, lw=0.5, zorder=8)
    ax.plot([x, xx - 8], [z2, z2], color=INK, lw=0.5, zorder=8)
    ax.plot([xx, xx], [lo, hi], color=INK, lw=0.7, zorder=8)
    ax.plot([xx - 5, xx + 5], [lo, lo], color=INK, lw=0.7, zorder=8)
    ax.plot([xx - 5, xx + 5], [hi, hi], color=INK, lw=0.7, zorder=8)
    ax.text(xx - 12, (lo + hi) / 2, text, ha="right", va="center",
            fontproperties=FONTB, fontsize=fs, color=INK, zorder=9, rotation=90)


def dim_h_below(ax, x1, x2, z, text, dz=55, fs=9.5):
    zz = z - dz
    ax.plot([x1, x1], [z, zz - 8], color=INK, lw=0.5, zorder=8)
    ax.plot([x2, x2], [z, zz - 8], color=INK, lw=0.5, zorder=8)
    ax.plot([x1, x2], [zz, zz], color=INK, lw=0.7, zorder=8)
    ax.plot([x1, x1], [zz - 5, zz + 5], color=INK, lw=0.7, zorder=8)
    ax.plot([x2, x2], [zz - 5, zz + 5], color=INK, lw=0.7, zorder=8)
    ax.text((x1 + x2) / 2, zz - 12, text, ha="center", va="top",
            fontproperties=FONTB, fontsize=fs, color=INK, zorder=9)


def dim_align(ax, x0, x1, z, text, color=ACCENT, fs=8.5):
    ax.plot([x0, x1], [z, z], color=color, lw=0.6, ls=(0, (2.5, 2.2)), zorder=7)
    ax.text(x1 + 10, z, text, ha="left", va="center",
            fontproperties=FONT, fontsize=fs, color=color, zorder=9)


def ground(ax, x0, x1, z=0):
    ax.plot([x0, x1], [z, z], color=INK, lw=1.1, zorder=2)
    for xx in np.linspace(x0, x1, 22):
        ax.plot([xx, xx - 10], [z, z - 10], color=INK, lw=0.4, zorder=2)
    ax.text((x0 + x1) / 2, z - 22, "GL", ha="center", va="top",
            fontproperties=FONT, fontsize=7, color=THIN, zorder=9)


def title_bar(ax, x0, x1, z, left, right):
    ax.add_patch(mpatches.Rectangle((x0, z), x1 - x0, 36,
                                    facecolor="#2C241C", edgecolor="none", zorder=20))
    ax.text(x0 + 16, z + 18, left, fontproperties=FONTB, fontsize=9.5,
            color="#F4EFE6", va="center", zorder=21)
    ax.text(x1 - 16, z + 18, right, fontproperties=FONT, fontsize=7.5,
            color="#F4EFE6", va="center", ha="right", zorder=21)


def standing_figure(ax, x, h, facing=1, fc=FIG):
    """Smooth architectural scale figure (side). x = heel, z=0."""
    from draw_cad_3view import catmull
    f = facing

    def p(dx, zh):
        return [x + f * dx * h, zh * h]

    body = [
        p(0.00, 0.00), p(0.06, 0.00), p(0.125, 0.012), p(0.11, 0.038),
        p(0.048, 0.07), p(0.05, 0.26), p(0.048, 0.47), p(0.03, 0.52),
        p(0.04, 0.68), p(0.07, 0.80), p(0.06, 0.84),
        p(0.035, 0.87), p(0.03, 0.935), p(0.07, 0.998), p(0.12, 0.978),
        p(0.135, 0.92), p(0.11, 0.86), p(0.08, 0.835),
        p(0.03, 0.80), p(-0.012, 0.66), p(-0.018, 0.515),
        p(0.00, 0.27), p(-0.018, 0.07), p(0.00, 0.00),
    ]
    fill_curve(ax, catmull(body, n=12, closed=True), fc, "none", lw=0, z=6, alpha=FIG_A)
    arm = [
        p(0.08, 0.80), p(0.13, 0.79), p(0.16, 0.68), p(0.15, 0.56),
        p(0.12, 0.525), p(0.10, 0.54), p(0.11, 0.62), p(0.10, 0.74),
        p(0.07, 0.79),
    ]
    fill_curve(ax, catmull(arm, n=10, closed=True), fc, "none", lw=0, z=7, alpha=FIG_A)


def lounge_figure(ax, fx):
    """Reclined lounge sitter, facing +x (front of chair). fx maps chair-y → plot x."""
    # Chair space: y=0 front, y=960 back, z=height. Plot x = fx(y).
    hip = np.array([fx(505), 408])
    sh = np.array([fx(655), 628])
    head = np.array([fx(708), 738])
    neck = (head + sh) / 2
    knee = np.array([fx(250), 392])
    ankle = np.array([fx(95), 52])
    toe = np.array([fx(18), 10])
    elbow = np.array([fx(520), 548])
    wrist = np.array([fx(390), 498])
    fc = FIG
    # torso + pelvis
    ax.add_patch(Circle(hip, 52, facecolor=fc, edgecolor="none", alpha=FIG_A, zorder=6))
    capsule(ax, hip, sh, 46, fc=fc)
    capsule(ax, sh, neck, 22, fc=fc)
    ax.add_patch(Ellipse(head, 78, 96, angle=-18,
                         facecolor=fc, edgecolor="none", alpha=FIG_A, zorder=7))
    # legs
    capsule(ax, hip, knee, 40, fc=fc)
    capsule(ax, knee, ankle, 28, fc=fc)
    capsule(ax, ankle, toe, 12, fc=fc)
    ax.add_patch(Ellipse((fx(48), 16), 70, 22, angle=-8,
                         facecolor=fc, edgecolor="none", alpha=FIG_A, zorder=6))
    # arm on thigh / armrest — lounge, not dining-upright
    capsule(ax, sh + np.array([0, -8]), elbow, 22, fc=fc)
    capsule(ax, elbow, wrist, 18, fc=fc)
    ax.add_patch(Ellipse(wrist, 28, 20, angle=-25,
                         facecolor=fc, edgecolor="none", alpha=FIG_A, zorder=6))


def save(fig, path):
    fig.savefig(path, dpi=DPI, facecolor=PAPER, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", path, path.stat().st_size)


def draw_wave():
    fig, ax = plt.subplots(figsize=(12.4, 7.4), dpi=DPI, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.set_aspect("equal")
    ax.axis("off")

    def fx(y):
        return D - y  # back to the left, matches sit photo

    def flip(xy):
        p = np.array(xy, float)
        p[:, 0] = D - p[:, 0]
        return p

    fill_curve(ax, flip(side_outer()), WOOD, WOOD_EDGE, lw=1.15, z=3)
    fill_curve(ax, flip(side_void()), "#FFFcf7", WOOD_EDGE, lw=0.7, z=4)
    fill_curve(ax, flip(side_pocket_lip()), WOOD, WOOD_EDGE, lw=0.6, z=4)
    fill_curve(ax, flip(side_cushion()), CUSH, CUSH_EDGE, lw=0.7, z=5)

    lounge_figure(ax, fx)

    x_back, x_front = fx(D), fx(0)
    ground(ax, x_back - 40, x_front + 80, 0)

    dim_v_left(ax, 0, H, x_back - 8, "820", dx=52)
    dim_v_left(ax, 0, ARM_H, x_back - 8, "580", dx=108)
    dim_v_left(ax, 0, SH_PAD, x_back - 8, "400", dx=164)
    dim_h_below(ax, x_back, x_front, 0, "960", dz=48)

    # effective seat depth — along the cushion, not through the knee
    ax.annotate("", xy=(fx(300), 455), xytext=(fx(300 + SEAT_D), 455),
                arrowprops=dict(arrowstyle="<->", color="#2E6B4F", lw=0.8), zorder=8)
    ax.text(fx(300 + SEAT_D / 2), 472, "520", color="#2E6B4F", ha="center",
            fontproperties=FONTB, fontsize=9, zorder=9)

    ax.annotate("", xy=(fx(500), 78), xytext=(fx(500), 78 + VOID_H),
                arrowprops=dict(arrowstyle="<->", color=THIN, lw=0.7), zorder=8)
    ax.text(fx(500) + 10, 78 + VOID_H / 2, "220", color=THIN,
            fontproperties=FONT, fontsize=8, va="center")

    ax.add_patch(Arc((fx(760), 700), 130, 130, theta1=70, theta2=92,
                     color=ACCENT, lw=1.0, zorder=8))
    ax.text(70, 805, "20°", color=ACCENT,
            fontproperties=FONTB, fontsize=9.5, zorder=9)

    ax.add_patch(Arc((fx(240), 400), 150, 150, theta1=0, theta2=5,
                     color=ACCENT, lw=1.0, zorder=8))
    ax.text(fx(240) + 70, 430, "5°", color=ACCENT,
            fontproperties=FONTB, fontsize=9.5, zorder=9)

    # sheet frame + title
    x0, x1 = -210, 1090
    z0, z1 = -118, 910
    ax.add_patch(mpatches.Rectangle((x0, z0), x1 - x0, z1 - z0,
                                    fill=False, ec=INK, lw=1.1, zorder=20))
    title_bar(ax, x0, x1, z1 - 36, "WAVE-LC-001   LOUNGE  POSTURE",
              "ERGONOMIC  SIDE    1 : 10    mm")

    ax.text(x0 + 16, z0 + 18,
            "SH 400   ·   SD 520   ·   ARM 580   ·   H 820   ·   D 960   ·   back 20°   ·   seat 5°",
            fontproperties=FONT, fontsize=7.6, color=THIN, va="center", zorder=21)
    ax.text(x1 - 16, z0 + 18, "shoulder / back support  ·  not a headrest",
            fontproperties=FONT, fontsize=7.2, color=THIN, va="center", ha="right", zorder=21)

    ax.set_xlim(x0 - 4, x1 + 4)
    ax.set_ylim(z0 - 4, z1 + 4)
    save(fig, OUT / "WAVE-LC-001_ergo.png")


def draw_koala():
    fig, ax = plt.subplots(figsize=(12.4, 7.6), dpi=DPI, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.set_aspect("equal")
    ax.axis("off")

    # product at x=260, ground z=0. Heights mm.
    px = 260
    Htot = 1280
    # flower base Ø180, stacked ~50
    for i, z, rx, ry, fc in [
        (0, 8, 92, 14, "#C9A56E"),
        (1, 22, 88, 13, WOOD),
        (2, 36, 84, 12, "#E8D2AE"),
    ]:
        ax.add_patch(Ellipse((px, z), rx * 2, ry * 2, facecolor=fc,
                             edgecolor=WOOD_EDGE, lw=0.9, zorder=3))
    # posts 2 x 615
    ax.add_patch(FancyBboxPatch((px - 14, 42), 12, 615, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.9, zorder=4))
    ax.add_patch(FancyBboxPatch((px + 2, 42), 12, 615, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.9, zorder=4))
    ax.add_patch(FancyBboxPatch((px - 14, 42 + 615), 12, 615, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.9, zorder=4))
    ax.add_patch(FancyBboxPatch((px + 2, 42 + 615), 12, 615, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.9, zorder=4))
    # pegs 3 levels: 770 / 965 / 1170, 55°, side view shows L/R
    peg_z = [770, 965, 1170]
    for z in peg_z:
        ax.plot([px + 10, px + 108], [z, z + 42], color="#C4A06A", lw=5.5,
                solid_capstyle="round", zorder=5)
        ax.plot([px - 10, px - 108], [z + 8, z + 50], color="#C4A06A", lw=5.5,
                solid_capstyle="round", zorder=5)
        ax.add_patch(Circle((px + 108, z + 42), 7, facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.6, zorder=6))
        ax.add_patch(Circle((px - 108, z + 50), 7, facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.6, zorder=6))
    # koala plaque
    ax.add_patch(Ellipse((px + 36, 1180), 36, 44, facecolor="#D9C4A0",
                         edgecolor=WOOD_EDGE, lw=0.8, zorder=6))

    ground(ax, 40, 1560, 0)

    dim_v_left(ax, 0, Htot, px - 130, "1280", dx=48)
    for z, lab in [(770, "770"), (965, "965"), (1170, "1170")]:
        dim_align(ax, px + 120, px + 210, z, lab, color="#2E6B4F")

    # adult coat height reference
    ax.plot([40, 1560], [1650, 1650], color=ACCENT, lw=0.6, ls=(0, (4, 3)), zorder=2)
    ax.text(50, 1670, "1650  overcoat", fontproperties=FONT, fontsize=8, color=ACCENT)

    standing_figure(ax, 780, 1750, facing=1)
    ax.text(800, -42, "1750", ha="center", fontproperties=FONT, fontsize=8, color=THIN)
    standing_figure(ax, 1120, 1200, facing=1)
    ax.text(1140, -42, "1200", ha="center", fontproperties=FONT, fontsize=8, color=THIN)

    x0, x1, z0, z1 = 0, 1600, -110, 1860
    ax.add_patch(mpatches.Rectangle((x0, z0), x1 - x0, z1 - z0,
                                    fill=False, ec=INK, lw=1.1, zorder=20))
    title_bar(ax, x0, x1, z1 - 36, "KOALA-CR-001   REACH  HEIGHTS",
              "ERGONOMIC  ELEVATION    mm")
    ax.text(x0 + 16, z0 + 18,
            "peg 770 / 965 / 1170   ·   H 1280   ·   kids + short jackets   ·   not an overcoat rack",
            fontproperties=FONT, fontsize=7.6, color=THIN, va="center")

    ax.set_xlim(x0 - 4, x1 + 4)
    ax.set_ylim(z0 - 4, z1 + 4)
    save(fig, OUT / "無尾熊-衣帽架" / "KOALA-CR-001_ergo.png")


def draw_f180():
    fig, ax = plt.subplots(figsize=(12.4, 7.4), dpi=DPI, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.set_aspect("equal")
    ax.axis("off")

    x, w, h = 180, 560, 1150
    # tower body
    ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle="round,pad=0,rounding_size=28",
                                facecolor="#F4F1EA", edgecolor=WOOD_EDGE, lw=1.1, zorder=3))
    # shelves: top 220, then 405, then 405
    zs = [0, 405, 810, 1150]
    thick = [22, 18, 18, 22]
    for z, t in zip(zs, thick):
        zz = z if z < h else h - t
        ax.add_patch(FancyBboxPatch((x, zz - (0 if z == 0 else 0)), w, t if z != 0 else 22,
                                    boxstyle="round,pad=0,rounding_size=4",
                                    facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.8, zorder=4))
    # fix top cap
    ax.add_patch(FancyBboxPatch((x, h - 22), w, 22, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.8, zorder=5))
    ax.add_patch(FancyBboxPatch((x, 0), w, 22, boxstyle="round,pad=0,rounding_size=6",
                                facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.8, zorder=5))
    # mid shelves at 405 and 810
    ax.add_patch(mpatches.Rectangle((x + 8, 405 - 9), w - 16, 18,
                                    facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.7, zorder=5))
    ax.add_patch(mpatches.Rectangle((x + 8, 810 - 9), w - 16, 18,
                                    facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.7, zorder=5))
    # bins hint
    for bx, bz, bh in [(x + 40, 30, 170), (x + 300, 30, 170),
                       (x + 40, 430, 170), (x + 300, 430, 170)]:
        ax.add_patch(mpatches.Rectangle((bx, bz), 200, bh, facecolor="#EFE6D6",
                                        edgecolor=WOOD_EDGE, lw=0.5, zorder=4, alpha=0.85))

    ground(ax, 40, 1560, 0)
    dim_v_left(ax, 0, h, x - 10, "1150", dx=56)
    dim_align(ax, x + w + 8, x + w + 90, 1035, "220", color="#2E6B4F")
    dim_align(ax, x + w + 8, x + w + 90, 608, "405", color="#2E6B4F")
    dim_align(ax, x + w + 8, x + w + 90, 202, "405", color="#2E6B4F")
    dim_h_below(ax, x, x + w, 0, "560", dz=48)

    standing_figure(ax, 980, 1750, facing=-1)
    ax.text(960, -42, "1750", ha="center", fontproperties=FONT, fontsize=8, color=THIN)
    standing_figure(ax, 1280, 1200, facing=-1)
    ax.text(1260, -42, "1200", ha="center", fontproperties=FONT, fontsize=8, color=THIN)

    x0, x1, z0, z1 = 0, 1600, -118, 1860
    ax.add_patch(mpatches.Rectangle((x0, z0), x1 - x0, z1 - z0,
                                    fill=False, ec=INK, lw=1.1, zorder=20))
    title_bar(ax, x0, x1, z1 - 36, "F180-RC-001   REACH  /  BAYS",
              "ERGONOMIC  ELEVATION    mm")
    ax.text(x0 + 16, z0 + 18,
            "H 1150 standing storage   ·   bays 220 / 405 / 405   ·   not a desk",
            fontproperties=FONT, fontsize=7.6, color=THIN, va="center")

    ax.set_xlim(x0 - 4, x1 + 4)
    ax.set_ylim(z0 - 4, z1 + 4)
    save(fig, OUT / "旋轉繪圖櫃" / "F180-RC-001_ergo.png")


if __name__ == "__main__":
    draw_wave()
    draw_koala()
    draw_f180()
