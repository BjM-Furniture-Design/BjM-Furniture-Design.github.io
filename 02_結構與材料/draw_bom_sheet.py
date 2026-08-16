# -*- coding: utf-8 -*-
"""One-page A3 visual BOM matching WAVE-LC-001 drawing style."""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT = Path(__file__).resolve().parent
FONT = FontProperties(fname=r"C:\Windows\Fonts\msjh.ttc")
FONTB = FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc")

PAPER = "#FBF9F4"
INK = "#1B1B1B"
HEAD = "#2C241C"
ACCENT = "#8B5A2B"
THIN = "#6B6560"
LINE = "#C8C2B6"
OAK = "#E4C9A0"
CREAM = "#F3EFE6"
GREEN = "#2E6B4F"

ROWS = [
    ("WAVE-A01", "左殼", "結構木材", "白橡層積 500×900×220", "1", "件", "自製", 6200, "5 軸；最薄緣 >=22"),
    ("WAVE-B01", "右殼（對稱）", "結構木材", "白橡層積 500×900×220", "1", "件", "自製", 6200, "與 A01 同批選料"),
    ("WAVE-C01", "座盆／脊板", "結構木材", "白橡層積 560×620×80", "1", "件", "自製", 1500, "止口 8–10，藏軟包下"),
    ("WAVE-W09", "備料／補片", "結構木材", "同批白橡約 0.020 m³", "1", "批", "自製", 1000, "備料係數 1.15"),
    ("WAVE-J01", "圓榫／鬆榫", "接合件", "Ø8×40 或 Domino 8×50", "18", "支", "外購", 150, "間距 80–110"),
    ("WAVE-J02", "對位銷（工藝）", "接合件", "鋼銷 Ø8 h6", "4", "支", "外購", 40, "成品不留"),
    ("WAVE-H01", "隱藏調整腳墊", "五金", "Ø20–25，調程 ±3", "4", "顆", "外購", 120, "接地平面度 0.5"),
    ("WAVE-H02", "防刮氈墊", "五金", "Ø25 厚 3", "4", "片", "外購", 20, "H01 已附氈可省"),
    ("WAVE-H03", "軟包定位", "五金", "Dual Lock 或暗銷 4 點", "1", "套", "外購", 60, "坐墊可拆"),
    ("WAVE-G01", "層積膠", "膠合", "EPI / PVAc D4", "0.80", "kg", "外購", 200, "養護 >=4 h"),
    ("WAVE-G02", "結構組裝膠", "膠合", "環氧或高固形 PU", "0.08", "kg", "外購", 140, "端紋不用白膠"),
    ("WAVE-G03", "填孔劑", "膠合", "淺橡色", "0.04", "kg", "外購", 50, "上油前"),
    ("WAVE-F01", "硬質油", "塗裝", "Osmo / Rubio 類 2–3 遍", "0.17", "L", "外購", 280, "薄緣不做厚 PU"),
    ("WAVE-F02", "砂紙耗材", "塗裝", "80–320 一套", "1", "套", "外購", 110, "留砂 0.25–0.35"),
    ("WAVE-F03", "拋光／黏塵", "塗裝", "無紡布＋黏塵布", "1", "套", "外購", 35, ""),
    ("WAVE-U01", "成型坐墊泡棉", "軟包", "HR 55–70 kg/m³，60–90 厚", "1", "件", "外購", 1100, "打樣可 CNC 切"),
    ("WAVE-U02", "靠背成型泡棉", "軟包", "同 U01", "1", "件", "外購", 900, "腰椎做在泡棉"),
    ("WAVE-U03", "表布／皮革", "軟包", "頭層 1.0 m² 或超纖 1.3 m", "1", "套", "外購", 2800, "價差最大項"),
    ("WAVE-U04", "底布＋襯材", "軟包", "定型棉＋暗拉鍊 #5", "1", "套", "外購", 150, "退木唇 8–12"),
    ("WAVE-P01", "外箱", "包裝", "內徑約 1020×1080×900", "1", "只", "外購", 230, "拆裝出貨可改"),
    ("WAVE-P02", "EPE／護角", "包裝", "EPE 20–30 mm", "1", "套", "外購", 110, "保護前舌薄緣"),
    ("WAVE-P03", "袋／銘牌／說明", "包裝", "PE＋乾燥劑＋銘牌", "1", "套", "外購", 70, ""),
    ("WAVE-T01", "內盆陰模治具", "工裝攤提", "MDF／PU 1 套 ÷10", "0.10", "套", "自製", 1400, "總價 8–20k"),
    ("WAVE-T02", "組裝對位治具", "工裝攤提", "鋼治具 1 套 ÷10", "0.10", "套", "自製", 700, "總價 4–12k"),
]

CAT_COLOR = {
    "結構木材": "#E8D4B5",
    "接合件": "#D9E2D4",
    "五金": "#D4DCE6",
    "膠合": "#E6DCC8",
    "塗裝": "#E8D9C8",
    "軟包": "#F0EBE3",
    "包裝": "#E4E4E0",
    "工裝攤提": "#EDE4D8",
}

CAT_SUM = {
    "結構木材": 14900,
    "接合件": 190,
    "五金": 200,
    "膠合": 390,
    "塗裝": 425,
    "軟包": 4950,
    "包裝": 410,
    "工裝攤提": 2100,
}


def draw():
    fig = plt.figure(figsize=(16.5354, 11.6929), dpi=200, facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(PAPER)

    ax.add_patch(mpatches.Rectangle((8, 8), 404, 281, fill=False, ec=INK, lw=0.9, zorder=20))
    ax.add_patch(mpatches.Rectangle((10, 10), 400, 277, fill=False, ec=INK, lw=0.35, zorder=20))

    ax.add_patch(mpatches.Rectangle((10, 276), 400, 11, facecolor=HEAD, edgecolor="none", zorder=21))
    ax.text(14, 281.5, "WAVE  LOUNGE  CHAIR    工程用料清單  EBOM",
            fontproperties=FONTB, fontsize=10, color="#F4EFE6", va="center", zorder=22)
    ax.text(406, 281.5, "WAVE-LC-001    Rev.A    2026-08-16    單位 NT$／mm    1 椅基準",
            fontproperties=FONT, fontsize=7.0, color="#F4EFE6", va="center", ha="right", zorder=22)

    # info chips
    chips = [
        (14, "成品", "900 × 960 × 820"),
        (86, "主結構", "A 左殼 ＋ B 右殼 ＋ C 座盆"),
        (186, "主材", "白橡層積  含水 8–10%"),
        (278, "成本基準", "小量 10 件／件，工裝已攤"),
        (360, "狀態", "概念  3D 未凍結"),
    ]
    for x, lab, val in chips:
        ax.text(x, 272.2, lab, fontproperties=FONT, fontsize=5.6, color=THIN, va="center", zorder=5)
        ax.text(x, 268.6, val, fontproperties=FONTB, fontsize=6.6, color=INK, va="center", zorder=5)
    ax.plot([14, 406], [265.6, 265.6], color=LINE, lw=0.4)

    # table geometry
    x0, y_top = 14, 263.5
    # columns: # pn name spec qty unit src amount note
    widths = [8, 28, 42, 78, 16, 12, 14, 22, 70]
    headers = ["#", "料號", "名稱", "規格／毛坯", "數量", "單位", "來源", "金額（中）", "備註"]
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)
    row_h = 8.15
    # header
    ax.add_patch(mpatches.Rectangle((x0, y_top - 7.2), sum(widths), 7.2,
                                    facecolor=HEAD, edgecolor="none", zorder=4))
    for i, h in enumerate(headers):
        ax.text((xs[i] + xs[i + 1]) / 2, y_top - 3.6, h,
                fontproperties=FONTB, fontsize=6.0, color="#F4EFE6",
                ha="center", va="center", zorder=5)

    for i, row in enumerate(ROWS):
        y = y_top - 7.2 - (i + 1) * row_h
        bg = CAT_COLOR[row[2]]
        ax.add_patch(mpatches.Rectangle((x0, y), sum(widths), row_h,
                                        facecolor=bg, edgecolor="none", zorder=3))
        ax.plot([x0, x0 + sum(widths)], [y, y], color=LINE, lw=0.25, zorder=4)
        pn, name, cat, spec, qty, unit, src, amt, note = row
        vals = [str(i + 1), pn, name, spec, qty, unit, src, f"{amt:,}", note]
        ha = ["center", "center", "left", "left", "center", "center", "center", "right", "left"]
        pad = [0, 0, 1.2, 1.2, 0, 0, 0, -1.4, 1.2]
        for j, (v, a, p) in enumerate(zip(vals, ha, pad)):
            tx = (xs[j] + xs[j + 1]) / 2 if a == "center" else (xs[j] + p if a == "left" else xs[j + 1] + p)
            ax.text(tx, y + row_h / 2, v, fontproperties=FONTB if j in (1, 7) else FONT,
                    fontsize=5.8, color=INK, ha=a, va="center", zorder=5, clip_on=True)
        # thin verticals
        for xv in xs:
            ax.plot([xv, xv], [y, y + row_h], color=LINE, lw=0.2, zorder=4)

    y_sum = y_top - 7.2 - (len(ROWS) + 1) * row_h
    total = sum(r[7] for r in ROWS)
    ax.add_patch(mpatches.Rectangle((x0, y_sum), sum(widths), row_h,
                                    facecolor=HEAD, edgecolor="none", zorder=4))
    ax.text(xs[7] - 2, y_sum + row_h / 2, "單椅材料＋工裝攤提小計（中位）",
            fontproperties=FONT, fontsize=6.4, color="#F4EFE6", ha="right", va="center", zorder=5)
    ax.text(xs[8] - 1.4, y_sum + row_h / 2, f"NT$ {total:,}",
            fontproperties=FONTB, fontsize=7.2, color="#F4EFE6", ha="right", va="center", zorder=5)

    # right? table is full width. Bottom summary cards
    yb = 14.5
    # category bars
    ax.text(16, 54.5, "成本結構（中位）", fontproperties=FONTB, fontsize=7.5, color=HEAD, va="center")
    cats = list(CAT_SUM.keys())
    vals = [CAT_SUM[c] for c in cats]
    mx = max(vals)
    bar_x0, bar_w, bar_h = 16, 118, 3.6
    for i, (c, v) in enumerate(zip(cats, vals)):
        y = 50.2 - i * 4.55
        ax.text(bar_x0, y + 1.7, c, fontproperties=FONT, fontsize=5.6, color=THIN, va="center")
        ax.add_patch(mpatches.Rectangle((bar_x0 + 28, y), bar_w * v / mx, bar_h,
                                        facecolor=CAT_COLOR[c], edgecolor=HEAD, lw=0.25, zorder=4))
        ax.text(bar_x0 + 28 + bar_w * v / mx + 1.6, y + bar_h / 2, f"{v:,}",
                fontproperties=FONT, fontsize=5.6, color=INK, va="center")

    # three number cards
    cards = [
        (178, "材料＋工裝（中）", "NT$ 23,565", "低 14,090　高 34,670"),
        (250, "小量製造成本（估）", "約 NT$ 48,000", "含人工／機時／8% 風險，未含管銷"),
        (322, "建議出廠底價", "NT$ 7–13 萬", "含管銷；利潤另加。打樣 12–20 萬"),
    ]
    for x, t, n, s in cards:
        ax.add_patch(FancyBboxPatch((x, 16), 68, 36, boxstyle="square,pad=0",
                                    facecolor=CREAM, edgecolor=HEAD, lw=0.45, zorder=3))
        ax.add_patch(mpatches.Rectangle((x, 46), 68, 6, facecolor=HEAD, edgecolor="none", zorder=4))
        ax.text(x + 34, 49, t, fontproperties=FONTB, fontsize=5.8, color="#F4EFE6",
                ha="center", va="center", zorder=5)
        ax.text(x + 34, 34, n, fontproperties=FONTB, fontsize=8.2, color=ACCENT,
                ha="center", va="center", zorder=5)
        ax.text(x + 34, 22.5, s, fontproperties=FONT, fontsize=5.3, color=THIN,
                ha="center", va="center", zorder=5, wrap=True)

    ax.text(16, 12.6,
            "※ 概念 EBOM，3D 未凍結不可直接下單。胡桃主材約＋15–30%。軟包 U03 為最大變數。人工／CAM 建模見 Excel「03_成本彙總」。",
            fontproperties=FONT, fontsize=5.6, color=THIN, va="center")

    png = OUT / "WAVE-LC-001_BOM_RevA.png"
    pdf = OUT / "WAVE-LC-001_BOM_RevA_sheet.pdf"
    fig.savefig(png, dpi=200, facecolor=PAPER)
    fig.savefig(pdf, facecolor=PAPER)
    plt.close(fig)
    print(png)
    print(pdf)


if __name__ == "__main__":
    draw()
