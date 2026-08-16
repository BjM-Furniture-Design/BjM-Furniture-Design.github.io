# -*- coding: utf-8 -*-
"""WAVE Lounge Chair — concept 3-view CAD sheet (A3, 1:10, 3rd angle)."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Polygon, PathPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent
FONT = FontProperties(fname=r"C:\Windows\Fonts\msjh.ttc")
FONTB = FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc")

# ---------------------------------------------------------------------------
# Locked concept dimensions (mm)
# ---------------------------------------------------------------------------
W, D, H = 900.0, 960.0, 820.0
SH_PAD, SH_WOOD, ARM_H = 400.0, 325.0, 580.0
SEAT_W, SEAT_D = 540.0, 520.0
VOID_H = 220.0
SCALE = 0.10  # 1:10

WOOD = "#E4C9A0"
WOOD_EDGE = "#3A2A18"
CUSH = "#F4F1EA"
CUSH_EDGE = "#B8B3A8"
VOID_FILL = "#FFFFFF"
INK = "#1B1B1B"
DIM = "#1B1B1B"
THIN = "#5A5A5A"
CL = "#2E6B4F"
PAPER = "#FBF9F4"
BLOCK = "#F3EFE6"
ACCENT = "#8B5A2B"

# ---------------------------------------------------------------------------
# Curve helpers
# ---------------------------------------------------------------------------
def catmull(pts, n=18, closed=False, alpha=0.5):
    pts = np.asarray(pts, float)
    if closed:
        pts = np.vstack([pts[-1], pts, pts[0], pts[1]])
    else:
        pts = np.vstack([pts[0], pts, pts[-1]])
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i : i + 4]
        d01 = np.linalg.norm(p1 - p0) ** alpha + 1e-9
        d12 = np.linalg.norm(p2 - p1) ** alpha + 1e-9
        d23 = np.linalg.norm(p3 - p2) ** alpha + 1e-9
        t = np.linspace(0, 1, n, endpoint=False)
        t2, t3 = t * t, t * t * t
        a = 2 * p1
        b = (p2 - p0) / d01 * d12
        # centripetal CR simplified (standard CR is fine for drawing)
        a = 2 * p1
        b = p2 - p0
        c = 2 * p0 - 5 * p1 + 4 * p2 - p3
        d = -p0 + 3 * p1 - 3 * p2 + p3
        seg = 0.5 * (a + b * t[:, None] + c * t2[:, None] + d * t3[:, None])
        out.append(seg)
    curve = np.vstack(out)
    if not closed:
        curve = np.vstack([curve, pts[-2]])
    else:
        curve = np.vstack([curve, curve[0]])
    return curve


def to_path(xy, closed=True):
    verts = xy.tolist()
    codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(verts) - 1)
    if closed:
        verts = verts + [verts[0]]
        codes = codes + [mpath.Path.CLOSEPOLY]
    return mpath.Path(verts, codes)


def fill_curve(ax, xy, fc, ec, lw=0.7, z=3, alpha=1.0, closed=True):
    ax.add_patch(PathPatch(to_path(xy, closed), facecolor=fc, edgecolor=ec,
                           lw=lw, alpha=alpha, zorder=z, joinstyle="round"))


def stroke_curve(ax, xy, ec, lw=0.6, ls="-", z=4, alpha=1.0):
    ax.plot(xy[:, 0], xy[:, 1], color=ec, lw=lw, ls=ls, zorder=z, alpha=alpha,
            solid_capstyle="round", solid_joinstyle="round")


# ---------------------------------------------------------------------------
# Geometry in chair space (mm).  x=width (0=CL), y=depth (0=front), z=height
# ---------------------------------------------------------------------------
def side_outer():
    """Right-side elevation outline (y, z). Front = y=0."""
    return catmull([
        (0, 52), (30, 18), (90, 0), (230, 0), (310, 18),
        (420, 36), (560, 28), (720, 8), (830, 0), (920, 6),
        (958, 48), (960, 110), (948, 240), (918, 400),
        (870, 560), (800, 690), (730, 775), (670, 818), (620, 820),
        (560, 800), (500, 740),
        (430, 680), (340, 640), (240, 610), (150, 560),
        (80, 430), (36, 260), (10, 130), (0, 52),
    ], n=16, closed=True)


def side_void():
    return catmull([
        (295, 70), (360, 125), (450, 195), (540, 228),
        (630, 200), (700, 145), (735, 95), (720, 62),
        (640, 48), (540, 58), (430, 52), (340, 48), (295, 70),
    ], n=14, closed=True)


def side_cushion():
    return catmull([
        (290, 355), (360, 348), (460, 352), (580, 370),
        (700, 430), (780, 540), (800, 650), (770, 740),
        (700, 790), (630, 788), (560, 730), (470, 620),
        (380, 500), (320, 420), (290, 355),
    ], n=14, closed=True)


def side_pocket_lip():
    """Inner wood lip around cushion (slightly larger than cushion)."""
    return catmull([
        (268, 338), (360, 328), (470, 332), (600, 352),
        (720, 420), (805, 540), (822, 660), (790, 760),
        (710, 812), (620, 808), (540, 740), (440, 610),
        (350, 480), (290, 390), (268, 338),
    ], n=14, closed=True)


def front_outer():
    """Front elevation (x, z), x=0 centerline."""
    right = [
        (0, 0), (210, 0), (340, 4), (420, 18), (450, 55),
        (430, 130), (360, 210), (310, 280), (300, 340),
        (330, 420), (400, 500), (450, 560), (448, 600),
        (410, 640), (360, 700), (280, 760), (170, 800), (0, 820),
    ]
    r = catmull(right, n=14, closed=False)
    l = np.column_stack([-r[::-1, 0], r[::-1, 1]])
    return np.vstack([r, l])


def front_void():
    """Under-seat opening seen from front."""
    right = [
        (0, 55), (160, 58), (250, 80), (280, 130),
        (250, 190), (170, 230), (0, 245),
    ]
    r = catmull(right, n=12, closed=False)
    l = np.column_stack([-r[::-1, 0], r[::-1, 1]])
    return np.vstack([r, l])


def front_cushion():
    right = [
        (0, 400), (180, 398), (250, 410), (270, 460),
        (250, 560), (200, 660), (120, 740), (0, 770),
    ]
    r = catmull(right, n=12, closed=False)
    l = np.column_stack([-r[::-1, 0], r[::-1, 1]])
    return np.vstack([r, l])


def front_seat_pad():
    """Lower seat cushion oval."""
    return catmull([
        (0, 400), (160, 398), (250, 410), (260, 445),
        (200, 470), (0, 478), (-200, 470), (-260, 445),
        (-250, 410), (-160, 398), (0, 400),
    ], n=12, closed=True)


def top_outer():
    """Top (x, y), y=0 front."""
    right = [
        (0, 0), (90, 8), (170, 30), (230, 80), (260, 150),
        (300, 260), (380, 360), (450, 430), (448, 520),
        (420, 640), (360, 780), (260, 900), (140, 945), (0, 960),
    ]
    r = catmull(right, n=14, closed=False)
    l = np.column_stack([-r[::-1, 0], r[::-1, 1]])
    return np.vstack([r, l])


def top_cushion():
    return catmull([
        (0, 250), (140, 255), (230, 290), (260, 380),
        (250, 520), (200, 680), (110, 780), (0, 800),
        (-110, 780), (-200, 680), (-250, 520), (-260, 380),
        (-230, 290), (-140, 255), (0, 250),
    ], n=12, closed=True)


def top_void():
    """Void visible as dashed inner opening near front-mid."""
    return catmull([
        (0, 160), (90, 170), (140, 210), (155, 280),
        (130, 340), (70, 370), (0, 378),
        (-70, 370), (-130, 340), (-155, 280), (-140, 210), (-90, 170), (0, 160),
    ], n=12, closed=True)


# ---------------------------------------------------------------------------
# Dimensioning
# ---------------------------------------------------------------------------
def arrow_pair(ax, p1, p2, color=DIM, lw=0.45):
    style = dict(arrowstyle="-|>", color=color, mutation_scale=7, lw=lw)
    ax.annotate("", xy=p2, xytext=p1, arrowprops=style, zorder=8)
    ax.annotate("", xy=p1, xytext=p2, arrowprops=style, zorder=8)


def dim_h(ax, x1, x2, y, text, dy=7.5, tick=1.6, font=7.2):
    ax.plot([x1, x1], [y - tick * 0.2, y + dy + tick], color=DIM, lw=0.35, zorder=8)
    ax.plot([x2, x2], [y - tick * 0.2, y + dy + tick], color=DIM, lw=0.35, zorder=8)
    yy = y + dy
    ax.plot([x1, x2], [yy, yy], color=DIM, lw=0.45, zorder=8)
    arrow_pair(ax, (x1, yy), (x2, yy))
    ax.text((x1 + x2) / 2, yy + 1.6, text, ha="center", va="bottom",
            fontproperties=FONT, fontsize=font, color=INK, zorder=9)


def dim_h_below(ax, x1, x2, y, text, dy=7.5, tick=1.6, font=7.2):
    ax.plot([x1, x1], [y + tick * 0.2, y - dy - tick], color=DIM, lw=0.35, zorder=8)
    ax.plot([x2, x2], [y + tick * 0.2, y - dy - tick], color=DIM, lw=0.35, zorder=8)
    yy = y - dy
    ax.plot([x1, x2], [yy, yy], color=DIM, lw=0.45, zorder=8)
    arrow_pair(ax, (x1, yy), (x2, yy))
    ax.text((x1 + x2) / 2, yy - 1.5, text, ha="center", va="top",
            fontproperties=FONT, fontsize=font, color=INK, zorder=9)


def dim_v(ax, z1, z2, x, text, dx=8.0, tick=1.6, font=7.2, text_out=2.1):
    lo, hi = min(z1, z2), max(z1, z2)
    ax.plot([x - tick * 0.2, x + dx + tick], [z1, z1], color=DIM, lw=0.35, zorder=8)
    ax.plot([x - tick * 0.2, x + dx + tick], [z2, z2], color=DIM, lw=0.35, zorder=8)
    xx = x + dx
    ax.plot([xx, xx], [lo, hi], color=DIM, lw=0.45, zorder=8)
    arrow_pair(ax, (xx, lo), (xx, hi))
    ax.text(xx + text_out, (lo + hi) / 2, text, ha="left", va="center",
            fontproperties=FONT, fontsize=font, color=INK, zorder=9, rotation=90)


def dim_v_left(ax, z1, z2, x, text, dx=8.0, tick=1.6, font=7.2, text_out=2.1):
    lo, hi = min(z1, z2), max(z1, z2)
    ax.plot([x + tick * 0.2, x - dx - tick], [z1, z1], color=DIM, lw=0.35, zorder=8)
    ax.plot([x + tick * 0.2, x - dx - tick], [z2, z2], color=DIM, lw=0.35, zorder=8)
    xx = x - dx
    ax.plot([xx, xx], [lo, hi], color=DIM, lw=0.45, zorder=8)
    arrow_pair(ax, (xx, lo), (xx, hi))
    ax.text(xx - text_out, (lo + hi) / 2, text, ha="right", va="center",
            fontproperties=FONT, fontsize=font, color=INK, zorder=9, rotation=90)


def ground_line(ax, x0, x1, y, label=True):
    ax.plot([x0, x1], [y, y], color=INK, lw=0.7, zorder=2)
    # hatch ticks
    for i, xx in enumerate(np.linspace(x0, x1, 18)):
        ax.plot([xx, xx - 1.6], [y, y - 1.6], color=INK, lw=0.28, zorder=2)
    if label:
        ax.text((x0 + x1) / 2, y - 3.4, "GL", ha="center", va="top",
                fontproperties=FONT, fontsize=6, color=THIN)


def view_label(ax, x, y, text):
    ax.text(x, y, text, ha="center", va="bottom", fontproperties=FONTB,
            fontsize=8.5, color=INK, zorder=10)
    w = 28
    ax.plot([x - w, x + w], [y - 1.2, y - 1.2], color=ACCENT, lw=0.9, zorder=10)


# ---------------------------------------------------------------------------
# Sheet
# ---------------------------------------------------------------------------
def draw_sheet():
    fig = plt.figure(figsize=(16.5354, 11.6929), dpi=220, facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(PAPER)

    # outer border
    ax.add_patch(mpatches.Rectangle((8, 8), 404, 281, fill=False,
                                    ec=INK, lw=0.9, zorder=20))
    ax.add_patch(mpatches.Rectangle((10, 10), 400, 277, fill=False,
                                    ec=INK, lw=0.35, zorder=20))

    # header bar
    ax.add_patch(mpatches.Rectangle((10, 276), 400, 11, facecolor="#2C241C",
                                    edgecolor="none", zorder=21))
    ax.text(14, 281.5, "WAVE  LOUNGE  CHAIR", fontproperties=FONTB,
            fontsize=10, color="#F4EFE6", va="center", zorder=22)
    ax.text(406, 281.5, "概念三視圖  CONCEPT  3-VIEW    第三角法    1 : 10    單位 mm",
            fontproperties=FONT, fontsize=7.2, color="#F4EFE6",
            va="center", ha="right", zorder=22)

    S = SCALE

    # ----- placement (paper mm) -----
    # Left stack: top + front.  Center: side.  Right column: title / table / notes.
    fx, fz0 = 66.0, 56.0
    sy0, sz0 = 164.0, 56.0
    tx, t_front_y = 66.0, 154.0

    # =====================================================================
    # FRONT VIEW
    # =====================================================================
    def xf(x):
        return fx + x * S

    def zf(z):
        return fz0 + z * S

    fo = front_outer()
    fv = front_void()
    fc = front_cushion()
    fs = front_seat_pad()
    fo_p = np.column_stack([xf(fo[:, 0]), zf(fo[:, 1])])
    fv_p = np.column_stack([xf(fv[:, 0]), zf(fv[:, 1])])
    fc_p = np.column_stack([xf(fc[:, 0]), zf(fc[:, 1])])
    fs_p = np.column_stack([xf(fs[:, 0]), zf(fs[:, 1])])

    fill_curve(ax, fo_p, WOOD, WOOD_EDGE, lw=0.85, z=3)
    fill_curve(ax, fv_p, "#FBF9F4", WOOD_EDGE, lw=0.55, z=4)
    fill_curve(ax, fc_p, CUSH, CUSH_EDGE, lw=0.5, z=5)
    fill_curve(ax, fs_p, "#FFFcf7", CUSH_EDGE, lw=0.45, z=6)
    # centerline
    ax.plot([xf(0), xf(0)], [zf(-18), zf(H + 12)], color=CL, lw=0.45,
            ls=(0, (3, 2, 0.7, 2)), zorder=7)
    ax.text(xf(0) + 2.2, zf(H + 14), "CL", fontproperties=FONT, fontsize=6, color=CL)
    ground_line(ax, xf(-W / 2 - 8), xf(W / 2 + 8), zf(0), label=False)

    # front dims
    dim_h_below(ax, xf(-W / 2), xf(W / 2), zf(0) - 1.5, "900", dy=8)
    dim_h(ax, xf(-SEAT_W / 2), xf(SEAT_W / 2), zf(SH_PAD) + 1.2, "540  座寬", dy=6.2, font=6.6)
    dim_v(ax, zf(0), zf(SH_PAD), xf(W / 2) + 2.0, "400  座高", dx=8.0, font=6.6)

    view_label(ax, xf(0), 20.5, "前視圖  FRONT")

    # =====================================================================
    # SIDE VIEW  (left side, front to the left — aligns with front view)
    # =====================================================================
    def ys(y):
        return sy0 + y * S

    def zs(z):
        return sz0 + z * S

    so = side_outer()
    sv = side_void()
    sl = side_pocket_lip()
    sc = side_cushion()
    so_p = np.column_stack([ys(so[:, 0]), zs(so[:, 1])])
    sv_p = np.column_stack([ys(sv[:, 0]), zs(sv[:, 1])])
    sl_p = np.column_stack([ys(sl[:, 0]), zs(sl[:, 1])])
    sc_p = np.column_stack([ys(sc[:, 0]), zs(sc[:, 1])])

    fill_curve(ax, so_p, WOOD, WOOD_EDGE, lw=0.85, z=3)
    fill_curve(ax, sl_p, "#D4B48A", WOOD_EDGE, lw=0.4, z=4)
    fill_curve(ax, sv_p, "#FBF9F4", WOOD_EDGE, lw=0.55, z=5)
    fill_curve(ax, sc_p, CUSH, CUSH_EDGE, lw=0.5, z=6)

    # seat / arm height helpers (thin)
    ax.plot([ys(250), ys(720)], [zs(SH_PAD), zs(SH_PAD)], color=THIN,
            lw=0.3, ls=(0, (2, 1.6)), zorder=7)
    ax.plot([ys(80), ys(280)], [zs(ARM_H), zs(ARM_H)], color=THIN,
            lw=0.3, ls=(0, (2, 1.6)), zorder=7)
    ax.plot([ys(260), ys(780)], [zs(SH_WOOD), zs(SH_WOOD - 18)], color=THIN,
            lw=0.3, ls=(0, (2, 1.6)), zorder=7)

    # back rake 20° reference
    # seat rake 5°
    ax.annotate("靠背傾 20°", xy=(ys(700), zs(760)), xytext=(ys(820), zs(700)),
                fontproperties=FONT, fontsize=6.2, color=THIN,
                arrowprops=dict(arrowstyle="-", color=THIN, lw=0.35), zorder=8)
    ax.annotate("座面後傾 5°", xy=(ys(520), zs(SH_PAD)), xytext=(ys(600), zs(455)),
                fontproperties=FONT, fontsize=6.2, color=THIN,
                arrowprops=dict(arrowstyle="-", color=THIN, lw=0.35), zorder=8)

    ground_line(ax, ys(-12), ys(D + 12), zs(0), label=True)

    dim_h_below(ax, ys(0), ys(D), zs(0) - 1.5, "960", dy=8)
    dim_h(ax, ys(280), ys(800), zs(SH_PAD) + 0.8, "520  有效座深", dy=6.0, font=6.6)
    dim_v(ax, zs(0), zs(H), ys(D) + 2.0, "820", dx=8.0)
    dim_v(ax, zs(0), zs(ARM_H), ys(D) + 16.5, "580  扶手", dx=7.5, font=6.5)
    ax.text(ys(90), zs(SH_WOOD) + 3.2, "325  木盆高", fontproperties=FONT,
            fontsize=6.0, color=THIN, ha="left", zorder=8)
    # void height
    ax.text(ys(510), zs(148), "220\n負空間高", ha="center", va="center",
            fontproperties=FONT, fontsize=6.0, color=THIN, zorder=8)

    view_label(ax, ys(D / 2), 20.5, "側視圖  SIDE  （前端朝左）")

    # alignment band between front and side (ground + height)
    ax.plot([xf(W / 2) + 22, ys(0) - 18], [zf(0), zs(0)], color="#C8C2B6",
            lw=0.3, ls=(0, (1.2, 1.2)), zorder=1)
    ax.plot([xf(W / 2) + 22, ys(0) - 18], [zf(H), zs(H)], color="#C8C2B6",
            lw=0.3, ls=(0, (1.2, 1.2)), zorder=1)

    # =====================================================================
    # TOP VIEW  (third angle: above front; chair-front at bottom of this graphic)
    # =====================================================================
    def xt(x):
        return tx + x * S

    def yt(y):
        return t_front_y + y * S  # depth upward, back away from front view? 
        # front view top is ~52+82=134. Top view front at 150. Gap 16mm.
        # If depth goes UP, back is at 150+96=246. Header starts 276. OK.
        # BUT third angle wants front of top-view adjacent to front-view,
        # i.e. front of chair at BOTTOM of top graphic. Depth UP = back at top.
        # Adjacent: bottom of top = FRONT of chair, near TOP of front view
        # (which is the TOP of the chair). That's the usual sheet arrangement.

    to = top_outer()
    tc = top_cushion()
    tv = top_void()
    to_p = np.column_stack([xt(to[:, 0]), yt(to[:, 1])])
    tc_p = np.column_stack([xt(tc[:, 0]), yt(tc[:, 1])])
    tv_p = np.column_stack([xt(tv[:, 0]), yt(tv[:, 1])])

    fill_curve(ax, to_p, WOOD, WOOD_EDGE, lw=0.85, z=3)
    fill_curve(ax, tc_p, CUSH, CUSH_EDGE, lw=0.5, z=5)
    stroke_curve(ax, tv_p, THIN, lw=0.45, ls=(0, (2.2, 1.4)), z=6)
    ax.plot([xt(0), xt(0)], [yt(-8), yt(D + 8)], color=CL, lw=0.45,
            ls=(0, (3, 2, 0.7, 2)), zorder=7)
    # split line note
    ax.text(xt(8), yt(D) + 3.2, "分件中線  A / B 半殼", fontproperties=FONT,
            fontsize=6, color=CL, ha="left")

    dim_h(ax, xt(-W / 2), xt(W / 2), yt(D) + 2.0, "900", dy=6.5)
    dim_v(ax, yt(0), yt(D), xt(W / 2) + 1.5, "960", dx=7.2)
    dim_h_below(ax, xt(-SEAT_W / 2), xt(SEAT_W / 2), yt(250) - 0.5, "540", dy=5.5, font=6.4)
    dim_v_left(ax, yt(250), yt(250 + SEAT_D), xt(-SEAT_W / 2) - 1.0, "520", dx=6.5, font=6.4)

    # front / back tags
    ax.text(xt(0), yt(0) - 3.8, "前端", ha="center", va="top",
            fontproperties=FONT, fontsize=6, color=THIN)
    ax.text(xt(-W / 2) - 2.0, yt(D) - 4.0, "後端", ha="right", va="top",
            fontproperties=FONT, fontsize=6, color=THIN)

    view_label(ax, xt(0), yt(D) + 18.5, "俯視圖  TOP")

    # alignment from front CL up to top CL
    ax.plot([xf(0), xt(0)], [zf(H) + 20, yt(0) - 8], color="#C8C2B6",
            lw=0.3, ls=(0, (1.2, 1.2)), zorder=1)

    # =====================================================================
    # Right column: title block + key dimensions + notes
    # =====================================================================
    tbl_x, tbl_y, tbl_w, tbl_h = 292.0, 132.0, 114.0, 82.0
    ax.add_patch(FancyBboxPatch((tbl_x, tbl_y), tbl_w, tbl_h,
                                boxstyle="square,pad=0", facecolor=BLOCK,
                                edgecolor=INK, lw=0.45, zorder=3))
    ax.add_patch(mpatches.Rectangle((tbl_x, tbl_y + tbl_h - 8), tbl_w, 8,
                                    facecolor="#2C241C", edgecolor="none", zorder=4))
    ax.text(tbl_x + tbl_w / 2, tbl_y + tbl_h - 4, "鎖定控制尺寸  KEY DIMENSIONS",
            ha="center", va="center", fontproperties=FONTB, fontsize=6.6, color="#F4EFE6", zorder=5)

    rows = [
        ("總寬  W", "900"),
        ("總深  D", "960"),
        ("總高  H", "820"),
        ("座高（含墊）", "400"),
        ("木盆高", "325"),
        ("扶手高", "580"),
        ("座寬（內淨）", "540"),
        ("有效座深", "520"),
        ("負空間高（約）", "220"),
        ("靠背傾角", "18–22°"),
        ("座面後傾", "4–6°"),
        ("木殼薄緣", "22–35"),
    ]
    ax.text(tbl_x + 5, tbl_y + 68.5, "項目", fontproperties=FONTB, fontsize=6.0, color=ACCENT, zorder=5)
    ax.text(tbl_x + tbl_w - 5, tbl_y + 68.5, "mm / °", fontproperties=FONTB, fontsize=6.0,
            color=ACCENT, ha="right", zorder=5)
    ax.plot([tbl_x + 4, tbl_x + tbl_w - 4], [tbl_y + 66.0, tbl_y + 66.0], color="#C8C2B6", lw=0.4, zorder=5)
    for i, (k, v) in enumerate(rows):
        yy = tbl_y + 61.2 - i * 4.75
        ax.text(tbl_x + 5, yy, k, fontproperties=FONT, fontsize=6.0, color=INK, va="center", zorder=5)
        ax.text(tbl_x + tbl_w - 5, yy, v, fontproperties=FONTB, fontsize=6.2, color=INK,
                ha="right", va="center", zorder=5)

    # =====================================================================
    # Notes (right column, below table)
    # =====================================================================
    nx, ny, nw = 292.0, 16.0, 114.0
    ax.add_patch(mpatches.Rectangle((nx, ny), nw, 112, facecolor="#FFFcf7",
                                    edgecolor=INK, lw=0.4, zorder=3))
    ax.add_patch(mpatches.Rectangle((nx, ny + 104), nw, 8,
                                    facecolor="#2C241C", edgecolor="none", zorder=4))
    ax.text(nx + nw / 2, ny + 108, "備註  NOTES", ha="center", va="center",
            fontproperties=FONTB, fontsize=6.6, color="#F4EFE6", zorder=5)
    notes = [
        "1. 本圖為概念三視圖。有機曲面以控制尺寸與 3D 為準，輪廓為概略。",
        "2. 投影：第三角法。比例 1:10。單位 mm。",
        "3. 未注公差：線形 ±1.0，曲面輪廓 ±1.5。",
        "4. 分件：左殼 A ＋ 右殼 B ＋ 座盆 C。止口藏軟包下。",
        "5. 材質：白橡層積實木，單層 22–28 mm，含水 8–10%。",
        "6. 軟包：成型泡棉 60–90 mm，外輪廓退木唇 8–12 mm。",
        "7. 接地平面度 0.5 mm／全長；隱藏腳墊 Ø20–25，±3 mm。",
        "8. 打樣後以實坐修正座盆與靠背，再凍結 CAM。",
        "9. 本階段不等於施工圖，不可直接下料。",
    ]
    for i, line in enumerate(notes):
        ax.text(nx + 4.2, ny + 97.5 - i * 10.0, line, fontproperties=FONT, fontsize=5.7,
                color=INK, va="top", zorder=5, wrap=True)
        # manual wrap by keeping lines short

    # =====================================================================
    # Title block (top of right column)
    # =====================================================================
    bx, by, bw, bh = 292.0, 218.0, 114.0, 54.0
    ax.add_patch(mpatches.Rectangle((bx, by), bw, bh, facecolor="#FFFcf7",
                                    edgecolor=INK, lw=0.55, zorder=4))
    # 4 rows × 2 cols
    rh = bh / 4
    for i in range(5):
        ax.plot([bx, bx + bw], [by + i * rh, by + i * rh], color=INK, lw=0.3, zorder=5)
    ax.plot([bx + 62, bx + 62], [by, by + 3 * rh], color=INK, lw=0.3, zorder=5)

    def cell(cx, row, label, value, width=60):
        cy = by + row * rh
        ax.text(bx + cx + 2.0, cy + rh - 3.4, label, fontproperties=FONT, fontsize=4.7,
                color=THIN, va="center", zorder=6)
        ax.text(bx + cx + 2.0, cy + 4.4, value, fontproperties=FONTB, fontsize=6.3,
                color=INK, va="center", zorder=6)

    cell(0, 3, "圖名  TITLE", "WAVE Lounge Chair")
    cell(0, 2, "圖號  DWG NO.", "WAVE-LC-001")
    cell(62, 2, "比例  SCALE", "1 : 10")
    cell(0, 1, "材質  MATERIAL", "白橡層積實木")
    cell(62, 1, "版次  REV", "A")
    cell(0, 0, "日期  DATE", "2026-08-16")
    cell(62, 0, "單位  UNIT", "mm")

    # legend chips
    ax.add_patch(mpatches.Rectangle((16, 16), 7, 4.2, facecolor=WOOD, edgecolor=WOOD_EDGE, lw=0.4, zorder=6))
    ax.text(24.5, 18.1, "層積實木", fontproperties=FONT, fontsize=6, color=INK, va="center", zorder=6)
    ax.add_patch(mpatches.Rectangle((48, 16), 7, 4.2, facecolor=CUSH, edgecolor=CUSH_EDGE, lw=0.4, zorder=6))
    ax.text(56.5, 18.1, "軟包坐墊", fontproperties=FONT, fontsize=6, color=INK, va="center", zorder=6)
    ax.plot([80, 90], [18.1, 18.1], color=THIN, lw=0.6, ls=(0, (2, 1.2)), zorder=6)
    ax.text(91.5, 18.1, "負空間／隱藏線", fontproperties=FONT, fontsize=6, color=INK, va="center", zorder=6)
    ax.plot([128, 138], [18.1, 18.1], color=CL, lw=0.6, ls=(0, (3, 2, 0.7, 2)), zorder=6)
    ax.text(139.5, 18.1, "中心線／分件", fontproperties=FONT, fontsize=6, color=INK, va="center", zorder=6)

    png = OUT / "WAVE-LC-001_3view.png"
    pdf = OUT / "WAVE-LC-001_3view.pdf"
    fig.savefig(png, dpi=220, facecolor=PAPER)
    fig.savefig(pdf, facecolor=PAPER)
    plt.close(fig)
    print(png)
    print(pdf)


if __name__ == "__main__":
    draw_sheet()
