# -*- coding: utf-8 -*-
"""Generate 1000 labeled training plates for roles 02 / 03 / 04."""
from __future__ import annotations

import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PAPER = (247, 243, 236)
CARD = (255, 252, 247)
INK = (28, 25, 21)
MUTED = (122, 114, 104)
OAK = (139, 90, 43)
LINE = (228, 221, 210)
GOOD = (46, 107, 79)
TERR = (176, 106, 84)
W, H = 1280, 800

BOOKS = {
    "02": "Pheasant Bodyspace / Ching Form Space Order / Pye Workmanship",
    "03": "Hoadley Understanding Wood / FPL Wood Handbook / Eckelman Furniture Strength",
    "04": "Kalpakjian Manufacturing / Smid CNC Handbook / Flexner Wood Finishing",
}


def font(size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/msjhbd.ttc" if bold else "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


F24, F22, F18, F16, F14 = font(24, True), font(22, True), font(18), font(16), font(14)


def new_card(role: str, rid: str, title: str, foundation: str):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((32, 28, W - 32, H - 28), 18, fill=CARD, outline=LINE, width=2)
    badge = {"02": "02  FORM", "03": "03  STRUCTURE", "04": "04  PRODUCTION"}[role]
    d.rounded_rectangle((56, 48, 280, 88), 14, fill=(42, 36, 28))
    d.text((72, 56), badge, font=F16, fill=PAPER)
    d.text((300, 54), rid, font=F22, fill=OAK)
    d.text((56, 104), title, font=F24, fill=INK)
    d.line((56, 148, W - 56, 148), fill=LINE, width=2)
    d.rectangle((56, H - 110, W - 56, H - 52), fill=(239, 232, 220))
    d.text((72, H - 98), "FOUNDATION  基礎", font=F14, fill=OAK)
    d.text((72, H - 76), foundation, font=F16, fill=INK)
    return im, d


def draw_person(d, x, y, h, sit=False):
    head = 14
    d.ellipse((x - head, y, x + head, y + 2 * head), fill=INK)
    if sit:
        d.line((x, y + 2 * head, x - 8, y + h * 0.45), fill=INK, width=6)
        d.line((x - 8, y + h * 0.45, x + 36, y + h * 0.48), fill=INK, width=6)
        d.line((x + 36, y + h * 0.48, x + 40, y + h), fill=INK, width=6)
    else:
        d.line((x, y + 2 * head, x, y + h * 0.55), fill=INK, width=6)
        d.line((x, y + h * 0.55, x - 16, y + h), fill=INK, width=6)
        d.line((x, y + h * 0.55, x + 16, y + h), fill=INK, width=6)


def plate_human(d, kind: str, n: int):
    floor = 620
    d.line((80, floor, 1200, floor), fill=INK, width=2)
    vals = [380, 400, 420, 430, 450, 460][n % 6]
    if kind == "seat":
        d.rectangle((200, floor - vals * 0.55, 520, floor), outline=OAK, width=3)
        d.line((180, floor, 180, floor - vals * 0.55), fill=GOOD, width=2)
        d.text((90, floor - vals * 0.28), f"{vals} mm", font=F18, fill=GOOD)
        draw_person(d, 360, floor - vals * 0.55 - 80, 220, sit=True)
    elif kind == "depth":
        d.rectangle((240, 360, 240 + 280, floor), outline=OAK, width=3)
        d.line((240, 640, 520, 640), fill=GOOD, width=2)
        d.text((320, 650), f"seat depth {480 + (n % 5) * 10} mm", font=F16, fill=GOOD)
    elif kind == "reach":
        draw_person(d, 280, 260, 360, sit=False)
        y = 300 + (n % 4) * 40
        d.line((280, y, 620, y), fill=TERR, width=2)
        d.text((640, y - 10), f"reach {1100 + (n % 6) * 50} mm", font=F16, fill=TERR)
    else:
        draw_person(d, 400, 280, 340, sit=True)
        d.arc((300, 250, 700, 620), 200, 330, fill=OAK, width=3)
        d.text((720, 360), "lounge rake 18-22 deg", font=F18, fill=OAK)


def plate_form(d, kind: str, n: int):
    if kind == "line":
        pts = [(140 + i * 90, 280 + int(80 * math.sin((i + n) * 0.7))) for i in range(11)]
        d.line(pts, fill=OAK, width=4)
        d.text((140, 520), "control line: ground - void - peak", font=F18, fill=INK)
    elif kind == "prop":
        d.rectangle((180, 220, 180 + 160, 560), outline=INK, width=2)
        d.rectangle((380, 220, 380 + 260, 560), outline=OAK, width=3)
        d.rectangle((680, 220, 680 + 360, 560), outline=GOOD, width=2)
        d.text((180, 580), "1 : 1.6 : 2.25  (not decoration, a check)", font=F16, fill=MUTED)
    elif kind == "radius":
        r = [4, 8, 12, 18, 24, 32][n % 6]
        d.rounded_rectangle((220, 240, 620, 560), r * 2, outline=OAK, width=4)
        d.text((660, 360), f"touch radius R{r}", font=F22, fill=OAK)
        d.text((660, 400), "hand: 8-12   contact: >=18", font=F16, fill=MUTED)
    elif kind == "color":
        chips = [(196, 154, 98), (139, 90, 43), (90, 70, 48), (210, 186, 150), (232, 220, 200)]
        for i, c in enumerate(chips):
            d.rectangle((160 + i * 180, 280, 320 + i * 180, 500), fill=c, outline=LINE)
        d.text((160, 530), "oak family: do not mix batches", font=F18, fill=INK)
    else:
        d.rectangle((160, 260, 900, 600), outline=INK, width=2)
        d.rectangle((220, 400, 400, 600), fill=(228, 201, 160), outline=OAK)
        d.rectangle((520, 340, 820, 600), fill=(210, 186, 150), outline=OAK)
        d.text((160, 620), "object vs room: furniture must keep a path", font=F16, fill=MUTED)


def plate_struct(d, kind: str, n: int):
    if kind == "rings":
        cx, cy = 360, 400
        for i in range(7):
            d.ellipse((cx - 30 - i * 22, cy - 24 - i * 16, cx + 30 + i * 22, cy + 24 + i * 16), outline=OAK)
        d.line((cx, cy - 140, cx, cy + 140), fill=TERR, width=2)
        d.text((560, 320), "growth rings / grain direction", font=F18, fill=INK)
        d.text((560, 360), "load prefers to follow the grain", font=F16, fill=MUTED)
    elif kind == "mc":
        d.rectangle((160, 300, 1040, 380), outline=INK, width=2)
        w = 80 + (n % 9) * 80
        d.rectangle((160, 300, 160 + w, 380), fill=TERR)
        d.text((160, 420), f"moisture content mark  {6 + n % 10}%   target 8-12%", font=F18, fill=INK)
    elif kind == "joint":
        d.rectangle((200, 280, 520, 560), outline=OAK, width=3)
        d.rectangle((520, 360, 820, 480), fill=(228, 201, 160), outline=INK, width=3)
        d.text((200, 590), "tenon through / glue area is the real joint", font=F16, fill=MUTED)
    elif kind == "load":
        d.polygon([(240, 560), (400, 260), (560, 560)], outline=INK, width=3)
        d.line((400, 200, 400, 260), fill=TERR, width=4)
        d.polygon([(380, 220), (400, 196), (420, 220)], fill=TERR)
        d.text((620, 320), "force in  /  force out  /  thinnest point", font=F18, fill=INK)
    else:
        d.ellipse((260, 280, 520, 540), outline=GOOD, width=3)
        d.text((300, 390), "cycle", font=F18, fill=GOOD)
        d.text((580, 340), f"furniture test  N = {10000 + (n % 8) * 5000}", font=F18, fill=INK)
        d.text((580, 380), "EN 1728 / BIFMA / ISO 7170", font=F16, fill=MUTED)


def plate_prod(d, kind: str, n: int):
    if kind == "flow":
        labels = ["PREP", "WHITE", "FINISH", "PACK"]
        for i, lb in enumerate(labels):
            x = 140 + i * 260
            d.rounded_rectangle((x, 300, x + 200, 500), 12, outline=OAK, width=3)
            d.text((x + 40, 380), lb, font=F18, fill=INK)
            if i < 3:
                d.polygon([(x + 210, 390), (x + 240, 400), (x + 210, 410)], fill=OAK)
    elif kind == "tool":
        d.polygon([(240, 260), (300, 260), (280, 560), (220, 560)], fill=(90, 90, 90))
        d.ellipse((250, 230, 290, 270), fill=OAK)
        d.text((360, 340), f"tool D{6 + (n % 8) * 2}  step {0.3 + (n % 5) * 0.1:.1f}", font=F18, fill=INK)
        d.text((360, 380), "leave 0.25-0.35 for sanding", font=F16, fill=MUTED)
    elif kind == "path":
        for i in range(14):
            y = 240 + i * 22
            d.arc((200, y, 900, y + 80), 200, 340, fill=OAK, width=2)
        d.text((200, 580), "sweep along the form, not XY slicing", font=F16, fill=MUTED)
    elif kind == "fix":
        d.rectangle((220, 420, 820, 560), fill=(180, 180, 180), outline=INK)
        d.ellipse((360, 300, 680, 460), outline=OAK, width=4)
        d.text((220, 590), "fixture first, toolpath second", font=F18, fill=INK)
    else:
        d.rectangle((200, 280, 520, 560), outline=INK, width=2)
        d.rectangle((220, 300, 500, 540), fill=(228, 201, 160))
        d.rectangle((600, 320, 1000, 560), outline=OAK, width=3)
        d.text((600, 280), "carton  +  EPE  +  orientation mark", font=F16, fill=MUTED)


def bank_02():
    rows = []
    human = [
        ("seat", "座高", "座面離地。lounge 常 380-420，餐椅 430-460。", "Tilley Measure of Man / Pheasant Bodyspace"),
        ("depth", "座深", "有效座深過長，小個子膝窩會頂到。", "Panero Human Dimension / Pheasant Bodyspace"),
        ("reach", "伸手", "掛衣、層板、畫具要對到第5百分位小孩與第95成人。", "Tilley Measure of Man / Cranz The Chair"),
        ("rake", "後傾", "休閒椅靠背 18-22°，不是餐椅正坐。", "Cranz The Chair / Postell Furniture Design"),
    ]
    for i in range(80):
        k, t, w, f = human[i % 4]
        rows.append(("human-" + k, f"{t}訓練 {i+1:02d}", w, f, k, i))
    form = [
        ("line", "控制線", "先有線，再有面。", "Ching Form Space and Order"),
        ("prop", "比例校核", "三個矩形並置，看誰在搶。", "Wong Principles of Form / Rams Less but Better"),
        ("radius", "倒圓", "手觸與結構圓角不是同一個 R。", "Pye Workmanship / Norman Everyday Things"),
        ("color", "木色家族", "同批對色，避免左右殼色差。", "Itten Art of Color / Albers Interaction of Color"),
        ("scene", "場景尺度", "家具必須讓出路。", "Ching Interior Design Illustrated / Alexander Pattern Language"),
    ]
    for i in range(180):
        k, t, w, f = form[i % 5]
        rows.append(("form-" + k, f"{t} {i+1:02d}", w, f, k, i))
    extra = [
        "浪形椅接地線", "負空間是否可讀", "扶手開口正視", "木布分模退唇", "花座五瓣節奏",
        "掛鉤 120° 陣列", "熊牌尺度", "繪圖櫃 R180 家族", "層板外伸當把手", "兒童 vs 成人視線",
        "客廳走道 900", "玄關短掛", "酒店大堂尺度", "觸覺先於照片", "少即是清楚",
    ]
    founds = [
        "Ching Form Space and Order", "Pye Nature of Workmanship", "Rams Less but Better",
        "Postell Furniture Design", "Pallasmaa Eyes of the Skin",
    ]
    for i in range(80):
        rows.append(("form-line", extra[i % len(extra)] + f" {i+1:02d}", "對現有 SKU 做外型複查。", founds[i % 5], "line", i))
    return rows  # 340


def bank_03():
    rows = []
    kinds = [
        ("rings", "年輪與受力", "力順著紋走，橫紋是弱向。", "Hoadley Understanding Wood / FPL Wood Handbook"),
        ("mc", "含水率", "8-12% 對應室內平衡含水，不是隨便寫。", "Hoadley Understanding Wood / FPL Wood Handbook"),
        ("joint", "接合面積", "膠線與榫肩才是節點，釘子只是夾緊。", "Eckelman Furniture Strength / Rogowski Joinery"),
        ("load", "力流", "進、出、最窄。斷在最窄。", "Hibbeler Mechanics of Materials / Gordon Structures"),
        ("test", "試驗次數", "家具有自己的循環，不是大樓規範。", "EN 1728 / BIFMA X5.1 / Eckelman"),
    ]
    labels = [
        "白橡導管", "橡膠木均質", "松木20mm", "山毛櫸移動", "胡桃色重",
        "端紋封油", "徑切 vs 弦切", "節疤避開受拉", "層積順紋", "指接接頭",
        "圓榫 H7", "Domino", "螺紋牙對橫紋", "軸承鎖", "牆扣路徑",
        "前舌不懸臂", "花座傾覆", "抽板偏載", "盆底32", "扶手根45",
    ]
    for i in range(330):
        k, t, w, f = kinds[i % 5]
        tag = labels[i % len(labels)]
        rows.append((k, f"{t} · {tag} {i+1:02d}", w + " " + tag, f, k, i))
    return rows


def bank_04():
    rows = []
    kinds = [
        ("flow", "四段工序", "備料白身噴漆包材，不要倒過來想。", "Kalpakjian Manufacturing / Joyce Furniture Making"),
        ("tool", "刀具", "直徑、步距、懸伸、留砂。", "Smid CNC Handbook / Machinery's Handbook"),
        ("path", "刀路", "順著形走，不要層切雕塑面。", "Choi Sculptured Surface Machining / NURBS Book"),
        ("fix", "治具", "先有夾，才有刀路。", "Boothroyd DFMA / Shingo SMED"),
        ("pack", "包材", "薄緣獨立保護，箱子要過運輸試驗。", "ISTA 3A / ASTM D4169 / Flexner Finishing"),
    ]
    tags = [
        "含水進料", "養料天數", "對色", "OP1基準", "真空吸盤",
        "陰模", "sweep", "球刀", "清根", "砂光工時",
        "硬質油", "EN71-3", "導管填孔", "拆裝說明", "EPE厚度",
        "五軸±40", "BACCI行程", "鑽模55度", "板式套裁", "換線",
        "粉塵", "VOC", "抽檢", "出廠攤治具", "客訴回饋",
    ]
    for i in range(330):
        k, t, w, f = kinds[i % 5]
        tag = tags[i % len(tags)]
        rows.append((k, f"{t} · {tag} {i+1:02d}", w, f, k, i))
    return rows


def render_one(role: str, idx: int, row, dest: Path):
    key, title, teach, found, kind, n = row
    rid = f"F{role}-{idx:04d}"
    im, d = new_card(role, rid, title, found)
    if role == "02":
        if key.startswith("human"):
            plate_human(d, kind, n)
        else:
            plate_form(d, kind, n)
    elif role == "03":
        plate_struct(d, kind, n)
    else:
        plate_prod(d, kind, n)
    d.text((56, 160), teach, font=F16, fill=MUTED)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=78, optimize=True)


def main():
    plans = [
        ("02", ROOT / "02_外型" / "訓練", bank_02()),
        ("03", ROOT / "03_結構與材料" / "訓練", bank_03()),
        ("04", ROOT / "04_生產與CNC" / "訓練", bank_04()),
    ]
    master = []
    for role, folder, rows in plans:
        img_dir = folder / "圖庫"
        img_dir.mkdir(parents=True, exist_ok=True)
        cat = folder / "圖目.csv"
        with cat.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "file", "title", "teaches", "foundation", "family"])
            for i, row in enumerate(rows, 1):
                fn = f"F{role}_{i:04d}.jpg"
                render_one(role, i, row, img_dir / fn)
                w.writerow([f"F{role}-{i:04d}", fn, row[1], row[2], row[3], row[0]])
                master.append((role, i, fn, row[1], row[3]))
                if i % 50 == 0:
                    print(role, i, flush=True)
        # split books
        src = ROOT / "訓練_書目_100本.csv"
        if src.exists():
            lines = src.read_text(encoding="utf-8").splitlines()
            head, body = lines[0], lines[1:]
            keep = [head] + [ln for ln in body if f",{role}," in f",{ln.split(',')[1]}," or ln.split(",")[1] == role]
            # safer filter
            keep = [head]
            for ln in body:
                parts = ln.split(",")
                if len(parts) > 1 and parts[1] == role:
                    keep.append(ln)
            (folder / "書目.csv").write_text("\n".join(keep) + "\n", encoding="utf-8")
        print("done", role, len(rows))
    with (ROOT / "訓練_圖目_1000.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["role", "n", "file", "title", "foundation"])
        w.writerows(master)
    print("TOTAL", len(master))


if __name__ == "__main__":
    main()
