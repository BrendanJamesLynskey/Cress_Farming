"""Generate the coloured SVG diagrams shared by the Cress Farming deck and report.

Run:  python3 diagrams/make_diagrams.py
Every figure sits on a cream 'paper' panel so it reads the same on the dark
presentation and on the white PDF pages. Part colours are consistent across
all figures: reel purple, knife red, guard blue, crank orange, ramp amber,
tank teal, motor gold/silver.
"""

import math
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "Inter, 'DejaVu Sans', Arial, sans-serif"

C = dict(
    bg="#FBF8F0", edge="#DDD5C2", ink="#1B2A4A", muted="#5A6673",
    green="#3E8E41", leaf="#6CC24A",
    bed="#EFE6CC", bededge="#D8CBA6", tub="#D6E6EE", tubedge="#7C9AAB",
    wood="#C68B59", woodedge="#8A5A33",
    knife="#E63946", knifedge="#A61E2A", guard="#4A9BE0", guardedge="#0B5CAD",
    crank="#F77F00", crankedge="#B85C00", reel="#B5179E",
    ramp="#FFB703", rampedge="#C98A00", tank="#2A9D8F", tankedge="#1F776C",
    tyre="#264653", cap="#E76F51", metal="#B8C0C8", metaledge="#6B7280",
    brass="#D4A017", brassedge="#9C7610", battery="#1F2937",
    red="#D62828", black="#111111", grey="#9CA3AF", foam="#FFFFFF", foamedge="#555555",
    pcb="#2E7D32",
)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = []
        self.markers = {}

    def raw(self, s):
        self.p.append(s)

    def marker(self, color):
        mid = "ah" + color.lstrip("#")
        if mid not in self.markers:
            self.markers[mid] = (
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        return mid

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.5, rx=0, op=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{d}/>')

    def circle(self, cx, cy, r, fill="none", stroke="none", sw=1.5, op=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}" opacity="{op}"{d}/>')

    def ellipse(self, cx, cy, rx, ry, fill, rot=0, stroke="none", sw=1):
        self.raw(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}" transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"/>')

    def line(self, x1, y1, x2, y2, stroke, sw=2, dash=None, cap="round", start=False, end=False, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if end:
            m += f' marker-end="url(#{self.marker(stroke)})"'
        if start:
            m += f' marker-start="url(#{self.marker(stroke)})"'
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                 f'stroke-width="{sw}" stroke-linecap="{cap}" opacity="{op}"{d}{m}/>')

    def path(self, d, stroke="none", sw=2, fill="none", dash=None, end=False, start=False, op=1, join="round"):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if end:
            m += f' marker-end="url(#{self.marker(stroke)})"'
        if start:
            m += f' marker-start="url(#{self.marker(stroke)})"'
        self.raw(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" stroke-linecap="round" '
                 f'stroke-linejoin="{join}" opacity="{op}"{ds}{m}/>')

    def poly(self, pts, fill, stroke="none", sw=1.5, op=1):
        s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.raw(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                 f'stroke-linejoin="round" opacity="{op}"/>')

    def text(self, x, y, s, size=14, weight=400, fill=None, anchor="start", rot=None):
        fill = fill or C["ink"]
        t = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                 f'text-anchor="{anchor}"{t}>{esc(s)}</text>')

    def label(self, x, y, title, sub=None, color=None, size=15):
        """Bold title with an optional muted second line; a coloured dot marks the part."""
        if color:
            self.circle(x - 12, y - 5, 5.5, fill=color, stroke="#00000033", sw=1)
        self.text(x, y, title, size=size, weight=700)
        if sub:
            self.text(x, y + 17, sub, size=12.5, fill=C["muted"])

    def leader(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, C["muted"], 1.3)
        self.circle(x2, y2, 3, fill=C["muted"])

    def badge(self, x, y, n, color):
        self.circle(x, y, 13, fill=color, stroke="#ffffff", sw=2)
        self.text(x, y + 5, str(n), size=13, weight=700, fill="#ffffff", anchor="middle")

    def cress(self, x0, y0, x1, y1, leaf=None, scale=1.0):
        leaf = leaf or C["leaf"]
        mx = (x0 + x1) / 2 + (x1 - x0) * 0.25
        my = (y0 + y1) / 2
        self.path(f"M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{y1:.1f}", C["green"], 2.2 * scale)
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) + 90
        for side in (-1, 1):
            a = math.radians(ang - 90 + side * 55)
            cx, cy = x1 + 7 * scale * math.cos(a), y1 + 7 * scale * math.sin(a)
            self.ellipse(cx, cy, 7.5 * scale, 4.2 * scale, leaf, rot=math.degrees(a))

    def sprig(self, x, y, rot=0, scale=0.8):
        a = math.radians(rot - 90)
        self.cress(x, y, x + 22 * scale * math.cos(a), y + 22 * scale * math.sin(a), scale=scale)

    def bg(self):
        self.rect(1, 1, self.w - 2, self.h - 2, fill=C["bg"], stroke=C["edge"], sw=2, rx=14)

    def save(self, name, title):
        body = "\n".join(self.p)
        defs = "<defs>" + "".join(self.markers.values()) + "</defs>"
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'font-family="{FONT}" role="img" aria-label="{esc(title)}">\n'
               f'<title>{esc(title)}</title>\n{defs}\n{body}\n</svg>\n')
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)


def n20(s, x, y, horizontal=False, scale=1.0):
    """Pictorial N20 gear motor. Vertical = shaft pointing down from (x, y) top-left."""
    k = scale
    if not horizontal:
        s.rect(x + 1, y, 24 * k, 6 * k, fill="#444")
        s.rect(x, y + 6 * k, 26 * k, 34 * k, fill=C["metal"], stroke=C["metaledge"], rx=3)
        s.rect(x - 2 * k, y + 40 * k, 30 * k, 22 * k, fill=C["brass"], stroke=C["brassedge"])
        s.line(x + 13 * k, y + 62 * k, x + 13 * k, y + 76 * k, "#555", 3.2 * k, cap="butt")
    else:
        s.rect(x, y + 2 * k, 6 * k, 24 * k, fill="#444")
        s.rect(x + 6 * k, y, 40 * k, 28 * k, fill=C["metal"], stroke=C["metaledge"], rx=3)
        s.rect(x + 46 * k, y - 2 * k, 26 * k, 32 * k, fill=C["brass"], stroke=C["brassedge"])
        s.line(x + 72 * k, y + 14 * k, x + 90 * k, y + 14 * k, "#555", 3.6 * k, cap="butt")


def wheel(s, cx, cy, r=45):
    s.circle(cx, cy, r, fill=C["tyre"])
    s.circle(cx, cy, r * 0.74, fill=C["cap"], stroke="#B4533A", sw=1.5)
    s.circle(cx, cy, 5, fill="#333")


def reel_wheel(s, cx, cy, r, paddle=11, sw=3, pw=7, start=15):
    for ang in (start, start + 90, start + 180, start + 270):
        a = math.radians(ang)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        s.line(cx, cy, ex, ey, C["reel"], sw)
        px, py = -math.sin(a) * paddle, math.cos(a) * paddle
        s.line(ex - px, ey - py, ex + px, ey + py, C["reel"], pw)


# ============================================================ 1. side view ===
# Scale ~3 px/mm. Rail top y=300 is level with the tray rim; the bed surface is
# 5 mm below it (y=315) and the knife runs 15 mm above the bed (y~270).
def side_view():
    s = SVG(900, 480)
    s.bg()
    random.seed(3)
    s.rect(30, 298, 840, 48, fill=C["tub"], stroke=C["tubedge"], rx=4)
    s.rect(34, 315, 832, 24, fill=C["bed"], stroke=C["bededge"])
    s.text(46, 366, "shallow tray · bed of folded damp kitchen paper, 5 mm below the rim", size=12, fill=C["muted"])
    for x in range(44, 166, 11):
        s.cress(x, 315, x + random.uniform(-6, 6), 315 - random.uniform(140, 160))
    for x in range(170, 196, 8):
        s.cress(x, 315, x + 30, 315 - random.uniform(105, 118))
    for x in range(208, 866, 11):
        s.line(x, 315, x + random.uniform(-1, 1), 272 + random.uniform(-2, 2), C["green"], 2.2)
    s.rect(30, 300, 840, 13, fill=C["wood"], stroke=C["woodedge"], op=0.85)
    s.text(270, 310.5, "wooden rail, top level with the tray rim", size=10.5, fill="#FFFFFF", weight=600)
    # header arm + reel strut (behind)
    for (x1, y1, x2, y2, w) in ((352, 180, 256, 258, 10), (352, 176, 150, 195, 7)):
        s.line(x1, y1, x2, y2, C["metaledge"], w)
        s.line(x1, y1, x2, y2, "#FFFFFF", w - 4.5)
    # chassis
    s.rect(480, 178, 315, 84, fill=C["foam"], stroke=C["foamedge"])
    s.rect(345, 171, 455, 7, fill="#E5E7EB", stroke=C["foamedge"], sw=1.2)
    # tank (dustpan shape) + ramp
    for x, rot in ((372, 60), (398, 80), (425, 70), (450, 85)):
        s.sprig(x, 250, rot, 0.75)
    s.poly([(330, 236), (330, 262), (470, 262), (470, 196)], C["tank"], C["tankedge"], 1.5, op=0.95)
    s.text(420, 252, "TANK", size=13, weight=700, fill="#FFFFFF", anchor="middle")
    s.poly([(250, 267), (256, 274), (336, 240), (330, 233)], C["ramp"], C["rampedge"], 1.5)
    s.sprig(292, 248, 70, 0.7)
    # plate D (cutter mount) + motor + crank
    s.rect(196, 252, 70, 7, fill=C["foam"], stroke=C["foamedge"], sw=1.2)
    n20(s, 207, 180)
    s.ellipse(220, 261, 17, 4.5, C["crank"], stroke=C["crankedge"])
    # cutter bar: guard under, knife on top
    s.poly([(250, 268), (250, 277), (200, 277), (170, 272.5), (200, 268)], C["guard"], C["guardedge"], 1.2)
    s.poly([(246, 262), (246, 268), (198, 268), (180, 265), (198, 262)], C["knife"], C["knifedge"], 1.2)
    # belt (outside face of the machine)
    s.line(150, 183, 520, 243, C["reel"], 2.2, dash="7 4")
    s.line(150, 207, 520, 267, C["reel"], 2.2, dash="7 4")
    # battery
    s.rect(560, 114, 150, 57, fill=C["battery"], rx=5)
    s.rect(670, 106, 24, 9, fill=C["grey"], rx=2)
    s.text(635, 148, "4 × AA · 6 V", size=14, weight=700, fill="#FFFFFF", anchor="middle")
    # wheels
    wheel(s, 520, 255)
    wheel(s, 745, 255)
    s.circle(520, 255, 12, stroke=C["reel"], sw=3)
    # reel
    reel_wheel(s, 150, 195, 48)
    s.circle(150, 195, 12, fill="#FFFFFF", stroke=C["reel"], sw=3)
    s.circle(150, 195, 3.5, fill=C["reel"])
    a1, a2 = math.radians(262), math.radians(198)
    s.path(f"M{150 + 64 * math.cos(a1):.1f},{195 + 64 * math.sin(a1):.1f} A64,64 0 0 0 "
           f"{150 + 64 * math.cos(a2):.1f},{195 + 64 * math.sin(a2):.1f}", C["reel"], 2.5, end=True)
    # handle, button, wires
    s.line(792, 176, 858, 84, C["wood"], 9)
    s.line(794, 168, 854, 84, C["red"], 1.8)
    s.rect(850, 72, 24, 12, fill=C["battery"], rx=2)
    s.circle(862, 68, 10, fill=C["knife"], stroke=C["knifedge"], sw=2)
    s.path("M562,126 C470,50 262,90 216,180", C["red"], 2.6)
    s.path("M562,140 C470,66 272,102 226,180", C["black"], 2.6)
    # cut height
    s.line(862, 272, 862, 315, C["ink"], 1.4, start=True, end=True)
    s.text(852, 366, "cut height ≈ 15 mm above the bed", size=12.5, weight=700, anchor="end")
    # travel + labels
    s.line(210, 34, 44, 34, C["ink"], 3, end=True)
    s.text(222, 39, "direction of travel", size=14, weight=600)
    s.label(50, 86, "Reel", "sweeps stems onto the knife", C["reel"])
    s.leader(92, 108, 128, 150)
    s.label(40, 430, "N20 motor + crank", "shaft points down", C["brass"])
    s.leader(110, 414, 206, 215)
    s.label(254, 430, "Cutter bar", "knife slides over guard", C["knife"])
    s.leader(262, 414, 214, 274)
    s.label(430, 430, "Ramp → tank", "cut cress slides in", C["ramp"])
    s.leader(440, 414, 300, 254)
    s.label(590, 430, "Belt", "wheels turn the reel", C["reel"])
    s.leader(600, 414, 330, 226)
    s.label(760, 430, "Wheels", "bottle caps", C["cap"])
    s.leader(770, 414, 745, 300)
    s.label(640, 40, "Hold-to-run button", None, C["knife"])
    s.leader(808, 46, 850, 66)
    s.save("side_view.svg", "Side view of the cress combine harvester with labelled parts")


# ============================================================ 2. plan view ===
def plan_view():
    s = SVG(900, 540)
    s.bg()
    random.seed(7)
    s.rect(60, 120, 800, 275, fill=C["tub"], stroke=C["tubedge"], rx=4)
    s.rect(68, 128, 784, 259, fill=C["bed"], stroke=C["bededge"])
    for _ in range(90):
        x, y = random.uniform(76, 166), random.uniform(136, 380)
        a = random.uniform(0, 180)
        dx, dy = 4 * math.cos(math.radians(a)), 4 * math.sin(math.radians(a))
        s.ellipse(x - dx, y - dy, 5, 3, C["leaf"], a)
        s.ellipse(x + dx, y + dy, 5, 3, C["leaf"], a)
    for _ in range(400):
        s.circle(random.uniform(240, 850), random.uniform(134, 382), 1.6, fill=C["green"])
    for yy in (93, 397):
        s.rect(60, yy, 800, 25, fill=C["wood"], stroke=C["woodedge"])
    # belt from reel pulley to front-axle pulley
    s.line(140, 74, 467, 74, C["reel"], 2.4, dash="7 4")
    s.line(140, 86, 467, 86, C["reel"], 2.4, dash="7 4")
    # header arms
    for yy in (125, 378):
        s.rect(140, yy, 292, 12, fill=C["foam"], stroke=C["foamedge"], sw=1.2)
    # plate D with guard + knife teeth poking forward
    s.rect(206, 132, 30, 338, fill=C["foam"], stroke=C["foamedge"], sw=1.2)
    for i in range(9):
        c = 157.5 + 25 * i
        s.poly([(206, c - 10), (206, c + 10), (172, c)], C["guard"], C["guardedge"], 1)
        s.poly([(206, c + 2.5), (206, c + 22.5), (182, c + 12.5)], C["knife"], C["knifedge"], 1, op=0.9)
    # pitman, crank, motor on the outrigger
    s.line(220, 372, 226, 436, C["wood"], 8)
    s.circle(232.5, 440, 17, fill=C["crank"], stroke=C["crankedge"])
    s.circle(220, 440, 4, fill=C["brass"], stroke=C["brassedge"], sw=1)
    s.rect(218, 426, 30, 26, fill=C["metal"], stroke=C["metaledge"], op=0.55, rx=2)
    # reel (ahead of the knife, over the uncut cress)
    s.line(140, 80, 140, 392, C["reel"], 3)
    s.rect(120, 145, 40, 225, fill=C["reel"], stroke=C["reel"], op=0.3)
    for yy in range(150, 370, 18):
        s.line(122, yy, 158, yy + 8, C["reel"], 1.2, op=0.7)
    s.rect(132, 72, 16, 16, fill=C["foam"], stroke=C["reel"], sw=2.5, rx=8)
    # ramp + tank
    s.rect(236, 145, 54, 225, fill=C["ramp"], stroke=C["rampedge"])
    for yy in range(170, 360, 40):
        s.path(f"M248,{yy + 10} L263,{yy} L278,{yy + 10}", C["rampedge"], 2, op=0.8)
    s.rect(290, 150, 140, 215, fill=C["tank"], stroke=C["tankedge"])
    s.text(360, 262, "TANK", size=15, weight=700, fill="#FFFFFF", anchor="middle")
    # chassis, axles, wheels
    for ax in (467, 657):
        s.line(ax, 86 if ax == 467 else 95, ax, 420, "#8B6F47", 4)
    s.rect(432, 125, 290, 265, fill=C["foam"], stroke=C["foamedge"], op=0.95)
    s.rect(455, 72, 24, 16, fill=C["foam"], stroke=C["reel"], sw=2.5, rx=8)
    for wx in (430, 620):
        for wy in (97, 398):
            s.rect(wx, wy, 75, 20, fill=C["tyre"], rx=3)
            s.rect(wx + 6, wy + 4, 63, 12, fill=C["cap"], rx=2)
    s.rect(535, 190, 115, 135, fill=C["battery"], rx=6)
    s.text(592, 254, "4 × AA", size=15, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(592, 273, "6 V", size=13, fill="#D1D5DB", anchor="middle")
    s.rect(722, 250, 118, 11, fill=C["wood"], stroke=C["woodedge"], rx=3)
    s.circle(852, 255, 11, fill=C["knife"], stroke=C["knifedge"], sw=2)
    s.path("M560,325 L560,456 L250,456", C["red"], 2.4)
    s.path("M568,325 L568,462 L246,462 L246,452", C["black"], 2.4)
    # dimensions
    s.line(36, 145, 36, 370, C["ink"], 1.3, start=True, end=True)
    s.text(26, 258, "cut width 90 mm", size=12.5, weight=700, anchor="middle", rot=-90)
    s.line(880, 105, 880, 410, C["ink"], 1.3, start=True, end=True)
    s.text(870, 258, "rails 120 mm apart (centres)", size=12.5, weight=700, anchor="middle", rot=-90)
    s.line(467, 490, 657, 490, C["ink"], 1.3, start=True, end=True)
    s.text(562, 484, "wheelbase 75 mm", size=12.5, weight=700, anchor="middle")
    s.line(120, 522, 722, 522, C["ink"], 1.3, start=True, end=True)
    s.text(421, 516, "machine ≈ 240 mm long, reel to back (plus the handle)", size=12.5, weight=700, anchor="middle")
    s.text(56, 494, "N20 + crank on an outrigger", size=12.5, weight=700, fill=C["brassedge"])
    s.leader(170, 480, 224, 446)
    s.line(250, 40, 80, 40, C["ink"], 3, end=True)
    s.text(262, 45, "direction of travel", size=14, weight=600)
    s.text(140, 64, "reel pulley", size=11.5, fill=C["reel"], weight=700, anchor="middle")
    s.text(467, 64, "front-axle pulley", size=11.5, fill=C["reel"], weight=700, anchor="middle")
    s.save("plan_view.svg", "Top view of the cress combine with dimensions")


# ======================================================= 3. cutter mechanism ===
def cutter_mechanism():
    s = SVG(900, 440)
    s.bg()
    s.rect(180, 150, 400, 40, fill=C["guard"], stroke=C["guardedge"])
    for i in range(10):
        cx = 200 + 40 * i
        s.poly([(cx - 16, 190), (cx + 16, 190), (cx, 270)], C["guard"], C["guardedge"])
    s.rect(170, 138, 430, 26, fill=C["knife"], stroke=C["knifedge"], op=0.88)
    for i in range(10):
        cx = 220 + 40 * i
        s.poly([(cx - 18, 164), (cx + 18, 164), (cx, 240)], C["knife"], C["knifedge"], op=0.82)
    for x in (250, 490):
        s.rect(x, 122, 30, 80, fill=C["grey"], stroke=C["metaledge"], op=0.92, rx=4)
        s.text(x + 15, 116, "hold-down", size=11.5, weight=700, fill=C["metaledge"], anchor="middle")
    s.line(610, 151, 740, 151, C["wood"], 16)
    s.circle(760, 151, 34, fill=C["crank"], stroke=C["crankedge"], sw=2)
    s.circle(760, 151, 6, fill="#555")
    for x in (610, 740):
        s.circle(x, 151, 6, fill=C["brass"], stroke=C["brassedge"], sw=1.5)
    s.rect(736, 131, 48, 40, fill="none", stroke=C["metaledge"], sw=2, dash="5 4")
    a1, a2 = math.radians(200), math.radians(320)
    s.path(f"M{760 + 50 * math.cos(a1):.1f},{151 + 50 * math.sin(a1):.1f} A50,50 0 0 1 "
           f"{760 + 50 * math.cos(a2):.1f},{151 + 50 * math.sin(a2):.1f}", C["crankedge"], 2.5, end=True)
    s.line(300, 92, 420, 92, C["knifedge"], 3, start=True, end=True)
    s.text(360, 80, "knife slides left ↔ right 10 mm", size=13.5, weight=700, fill=C["knifedge"], anchor="middle")
    s.text(760, 64, "N20 sits on top,", size=12.5, weight=700, anchor="middle")
    s.text(760, 80, "shaft down into the crank", size=12.5, fill=C["muted"], anchor="middle")
    s.text(675, 182, "pitman arm", size=12, weight=700, fill=C["woodedge"], anchor="middle")
    s.text(610, 128, "split pin", size=11, fill=C["muted"], anchor="middle")
    s.text(700, 216, "crank radius 5 mm", size=12.5, weight=700, anchor="middle")
    s.text(700, 232, "= 10 mm stroke", size=12.5, fill=C["muted"], anchor="middle")
    s.line(200, 292, 240, 292, C["ink"], 1.3, start=True, end=True)
    s.line(200, 272, 200, 298, C["ink"], 0.8, dash="2 2")
    s.line(240, 272, 240, 298, C["ink"], 0.8, dash="2 2")
    s.text(250, 297, "tooth pitch 10 mm", size=12.5, weight=700)
    s.line(60, 160, 60, 270, C["ink"], 3, end=True)
    s.text(60, 150, "FRONT", size=12.5, weight=700, anchor="middle")
    s.text(60, 290, "cress", size=12, fill=C["muted"], anchor="middle")
    # side section inset
    s.rect(560, 262, 320, 162, fill="#FFFFFF", stroke=C["edge"], rx=10)
    s.text(720, 284, "Side section — like scissor blades", size=13, weight=700, anchor="middle")
    s.line(690, 386, 690, 300, C["green"], 3)
    s.ellipse(683, 300, 8, 4.5, C["leaf"], -30)
    s.ellipse(698, 300, 8, 4.5, C["leaf"], 30)
    s.rect(740, 318, 120, 14, fill=C["foam"], stroke=C["foamedge"])
    s.text(800, 314, "mount plate", size=10.5, fill=C["muted"], anchor="middle")
    s.rect(800, 344, 60, 5, fill="#CBD5E1", stroke=C["metaledge"], sw=1)
    s.poly([(860, 349), (860, 358), (660, 358), (620, 353.5), (660, 349)], C["guard"], C["guardedge"])
    s.poly([(790, 335), (790, 344), (668, 344), (636, 339.5), (668, 335)], C["knife"], C["knifedge"])
    s.rect(740, 332, 50, 3, fill=C["grey"])
    s.text(580, 376, "knife (top)", size=11.5, weight=700, fill=C["knifedge"])
    s.text(580, 392, "guard (below)", size=11.5, weight=700, fill=C["guardedge"])
    s.text(830, 376, "spacer", size=10.5, fill=C["muted"], anchor="middle")
    s.text(720, 412, "the plate overhang holds the knife flat on the guard", size=11.5, fill=C["muted"], anchor="middle")
    y = 336
    for i, (col, name) in enumerate(((C["guard"], "Guard comb — fixed to the header, never moves"),
                                     (C["knife"], "Knife — slides side to side"),
                                     (C["crank"], "Crank — flat disc glued on the motor shaft"),
                                     (C["wood"], "Pitman arm — turns spin into slide"))):
        s.rect(40, y + 22 * i - 11, 18, 14, fill=col, rx=3)
        s.text(68, y + 22 * i, name, size=12.5)
    s.save("cutter_mechanism.svg", "Cutter bar mechanism: guard, knife, crank and pitman arm")


# =========================================================== 4. shear frames ===
def shear_frames():
    s = SVG(900, 290)
    s.bg()
    caps = (("1 · Gap open", "a stem slides into the V"),
            ("2 · Knife pushes", "stem is trapped against the guard"),
            ("3 · Edges cross", "snip! — a scissor cut"))
    for k, kc in enumerate((80, 124, 176)):
        ox = 20 + 290 * k
        s.rect(ox, 20, 280, 250, fill="#FFFFFF", stroke=C["edge"], rx=10)
        for gc in (80, 200):
            s.poly([(ox + gc - 48, 50), (ox + gc + 48, 50), (ox + gc, 190)], C["guard"], C["guardedge"])
        if k < 2:
            s.circle(ox + 140, 150, 7.5, fill=C["green"], stroke="#2A6B2D")
        else:
            s.ellipse(ox + 196, 128, 8, 4, C["green"], 40)
            s.ellipse(ox + 205, 142, 8, 4, C["green"], 40)
            s.text(ox + 214, 110, "snip!", size=14, weight=700, fill=C["knifedge"])
        s.poly([(ox + kc - 48, 50), (ox + kc + 48, 50), (ox + kc, 190)], C["knife"], C["knifedge"], op=0.72)
        if k < 2:
            s.line(ox + kc - 20, 70, ox + kc + 30, 70, "#FFFFFF", 3.5, end=True)
        s.text(ox + 140, 222, caps[k][0], size=15, weight=700, anchor="middle")
        s.text(ox + 140, 242, caps[k][1], size=12.5, fill=C["muted"], anchor="middle")
    s.save("shear_frames.svg", "How the knife shears a cress stem in three steps")


# =============================================================== 5. wiring ===
def wiring():
    s = SVG(900, 400)
    s.bg()
    s.rect(40, 120, 190, 150, fill=C["battery"], rx=8)
    for i in range(4):
        y = 134 + 32 * i
        s.rect(56, y, 150, 24, fill="#F4A261" if i % 2 == 0 else "#2A9D8F", rx=4)
        s.rect(206 if i % 2 == 0 else 50, y + 7, 6, 10, fill="#CBD5E1")
        s.text(131, y + 17, "AA  1.5 V", size=11.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(135, 296, "4 × AA = 6 V", size=15, weight=700, anchor="middle")
    s.text(135, 314, "(same as a toy car)", size=12, fill=C["muted"], anchor="middle")
    # fuse first, right after the battery
    s.circle(320, 162, 20, fill="#FFD166", stroke="#C99A2E", sw=2)
    s.text(320, 167, "PTC", size=10, weight=700, anchor="middle")
    s.rect(410, 142, 80, 40, fill=C["grey"], stroke=C["metaledge"], rx=4)
    s.rect(420, 150, 60, 24, fill="#4B5563", rx=3)
    s.rect(454, 152, 24, 20, fill="#E5E7EB", rx=2)
    s.text(466, 166, "ON", size=10, weight=700, anchor="middle")
    s.rect(555, 152, 50, 30, fill=C["battery"], rx=4)
    s.circle(580, 146, 15, fill=C["knife"], stroke=C["knifedge"], sw=2)
    n20(s, 700, 186, horizontal=True, scale=1.3)
    s.circle(703, 196, 4, fill=C["red"])
    s.circle(703, 220, 4, fill=C["black"])
    s.line(672, 196, 700, 196, "#777", 1.5)
    s.line(672, 220, 700, 220, "#777", 1.5)
    s.circle(668, 208, 11, fill="#E09F3E", stroke="#9A6A1F")
    s.text(668, 212, "104", size=8.5, weight=700, anchor="middle")
    s.path("M230,162 L300,162", C["red"], 4)
    s.path("M340,162 L410,162", C["red"], 4)
    s.path("M490,162 L520,162 L520,176 L555,176", C["red"], 4)
    s.path("M605,176 L640,176 L640,196 L703,196", C["red"], 4)
    s.path("M230,236 L640,236 L640,220 L703,220", C["black"], 4)
    for x, y in ((258, 150), (368, 150), (622, 164)):
        s.line(x - 8, y, x + 8, y, C["red"], 2, end=True)
    s.line(420, 250, 404, 250, C["black"], 2, end=True)
    s.badge(320, 108, 1, C["ink"])
    s.text(320, 70, "500 mA self-", size=13.5, weight=700, anchor="middle")
    s.text(320, 86, "resetting fuse", size=13.5, weight=700, anchor="middle")
    s.badge(450, 108, 2, C["ink"])
    s.text(450, 84, "ON / OFF switch", size=13.5, weight=700, anchor="middle")
    s.badge(580, 108, 3, C["ink"])
    s.text(580, 70, "hold-to-run", size=13.5, weight=700, anchor="middle")
    s.text(580, 86, "button", size=13.5, weight=700, anchor="middle")
    s.badge(770, 146, 4, C["ink"])
    s.text(770, 122, "N20 motor", size=13.5, weight=700, anchor="middle")
    s.badge(668, 262, 5, C["ink"])
    s.text(668, 290, "100 nF capacitor", size=13, weight=700, anchor="middle")
    s.text(668, 306, "(marked 104)", size=12, fill=C["muted"], anchor="middle")
    s.text(420, 272, "black wire back to the battery", size=12.5, fill=C["muted"], anchor="middle")
    s.text(380, 212, "red wire", size=12.5, weight=700, fill=C["red"], anchor="middle")
    s.rect(40, 330, 820, 54, fill="#FFFFFF", stroke=C["edge"], rx=8)
    s.text(60, 352, "One loop of wire. Break it anywhere — switch OFF, button let go, or the fuse tripping on a jam —",
           size=13.5, weight=600)
    s.text(60, 372, "and the knife stops. Swap the two motor wires to run the motor the other way (the crank doesn't mind).",
           size=13.5, fill=C["muted"])
    s.save("wiring.svg", "Wiring diagram: battery, fuse, switch, hold-to-run button and N20 motor")


# ============================================================ 6. templates ===
def templates():
    s = SVG(900, 690)
    s.bg()
    k = 2.0  # px per mm

    def part(x, y, w, h, title, dims, fill=C["foam"], stroke=C["foamedge"]):
        s.rect(x, y, w * k, h * k, fill=fill, stroke=stroke, sw=1.8)
        s.text(x, y - 8, title, size=13.5, weight=700)
        if dims:
            s.text(x + w * k / 2, y + h * k / 2 + 5, dims, size=12, fill=C["muted"], anchor="middle")

    s.text(30, 34, "Foam board (5 mm) — cut with a craft knife and steel ruler (grown-up job)", size=15, weight=700)
    part(30, 70, 140, 100, "A  Base plate", "140 × 100 mm")
    part(340, 70, 140, 40, "B  Side plates — cut 2", "140 × 40 mm")
    for hx in (35, 110):
        s.circle(340 + hx * k, 70 + 30 * k, 5, fill=C["bg"], stroke=C["foamedge"])
    s.text(340, 70 + 40 * k + 20, "Ø 5 mm straw holes, 10 mm up, 35 & 110 mm from the front", size=11.5, fill=C["muted"])
    part(650, 70, 110, 20, "C  Header arms — cut 2", "")
    for hx in (8, 18, 96):
        s.circle(650 + hx * k, 70 + 10 * k, 4, fill=C["bg"], stroke=C["foamedge"])
    s.text(650, 70 + 20 * k + 18, "110 × 20 mm · Ø 4 mm holes at", size=11.5, fill=C["muted"])
    s.text(650, 70 + 20 * k + 33, "8 & 18 mm (pins), 96 mm (reel)", size=11.5, fill=C["muted"])
    # D: cutter mount plate with the motor outrigger
    part(30, 340, 160, 30, "D  Cutter mount plate", "160 × 30 mm")
    s.rect(30 + 141 * k, 340 + 10 * k, 12 * k, 10 * k, stroke=C["brassedge"], sw=1.5, dash="4 3")
    s.circle(30 + 147 * k, 340 + 15 * k, 5, fill=C["bg"], stroke=C["foamedge"])
    s.text(30, 340 + 30 * k + 18, "Ø 5 mm shaft hole: 147 mm from the left,", size=11.5,
           fill=C["brassedge"], weight=600)
    s.text(30, 340 + 30 * k + 33, "15 mm from the back; motor in the dashed box", size=11.5, fill=C["brassedge"],
           weight=600)
    part(380, 340, 90, 40, "E  Ramp", "90 × 40 mm", fill="#FFF4D6", stroke=C["rampedge"])
    part(600, 340, 85, 15, "F  Reel paddles — cut 4", "", fill="#F6DDF1", stroke=C["reel"])
    s.text(600 + 85, 340 + 15 * k - 8, "85 × 15", size=11, fill=C["muted"], anchor="middle")
    for cx in (810, 856):
        s.circle(cx, 355, 20, fill="#F6DDF1", stroke=C["reel"], sw=1.8)
    s.text(833, 398, "Reel hubs Ø 20 × 2", size=11.5, fill=C["muted"], anchor="middle")
    s.text(380, 452, "K  Tank: a small plastic tub about 90 × 50 mm, front wall cut down", size=12.5, weight=700)
    s.text(380, 469, "to 8 mm so the ramp can tip cress in (a dustpan shape)", size=12, fill=C["muted"])

    s.text(30, 522, "Stiff plastic, 1 mm (e.g. a ring-binder cover) — strong scissors are fine", size=15, weight=700)
    gx, gy = 30, 556
    s.rect(gx, gy, 100 * k, 16 * k, fill=C["guard"], stroke=C["guardedge"])
    s.line(gx, gy + 8 * k, gx + 100 * k, gy + 8 * k, "#FFFFFF", 1.2, dash="4 3")
    for i in range(10):
        cx = gx + (5 + 10 * i) * k
        s.poly([(cx - 4 * k, gy + 16 * k), (cx + 4 * k, gy + 16 * k), (cx, gy + 31 * k)], C["guard"], C["guardedge"], 1)
    s.text(gx, gy - 8, "G  Guard comb", size=13.5, weight=700)
    s.text(gx, gy + 31 * k + 18, "100 mm · base 16 mm · 10 teeth 15 mm long", size=11.5, fill=C["muted"])
    s.text(gx, gy + 31 * k + 33, "dashed line: spacer strip (100 × 8 mm) goes here", size=11.5, fill=C["muted"])
    kx, ky = 300, 564
    s.rect(kx, ky, 112 * k, 6 * k, fill=C["knife"], stroke=C["knifedge"])
    for i in range(10):
        cx = kx + (5 + 10 * i) * k
        s.poly([(cx - 4.5 * k, ky + 6 * k), (cx + 4.5 * k, ky + 6 * k), (cx, ky + 18 * k)], C["knife"], C["knifedge"], 1)
    s.circle(kx + 107 * k, ky + 3 * k, 3, fill=C["bg"], stroke=C["knifedge"])
    s.text(kx, gy - 8, "H  Knife", size=13.5, weight=700)
    s.text(kx, ky + 18 * k + 18, "112 mm · base 6 mm · 10 teeth 12 mm long", size=11.5, fill=C["muted"])
    s.text(kx, ky + 18 * k + 33, "Ø 3 mm pin hole 5 mm from the long end", size=11.5, fill=C["muted"])
    px, py = 580, 578
    s.rect(px, py, 45 * k, 10 * k, fill=C["wood"], stroke=C["woodedge"], rx=10)
    s.circle(px + 5 * k, py + 5 * k, 3, fill=C["bg"])
    s.circle(px + 40 * k, py + 5 * k, 3, fill=C["bg"])
    s.text(px, gy - 8, "I  Pitman arm", size=13.5, weight=700)
    s.text(px, py + 38, "45 mm of lolly stick,", size=11.5, fill=C["muted"])
    s.text(px, py + 53, "holes 35 mm apart", size=11.5, fill=C["muted"])
    s.circle(800, 596, 20, fill=C["crank"], stroke=C["crankedge"], sw=2)
    s.circle(800, 596, 3, fill="#333")
    s.circle(790, 596, 3, fill=C["brass"], stroke=C["brassedge"])
    s.text(760, gy - 8, "J  Crank", size=13.5, weight=700)
    s.text(760, 636, "Ø 20 mm disc, pin hole", size=11.5, fill=C["muted"])
    s.text(760, 651, "5 mm off centre", size=11.5, fill=C["muted"])
    s.line(650, 262, 650 + 50 * k, 262, C["ink"], 3, cap="butt")
    s.line(650, 256, 650, 268, C["ink"], 2)
    s.line(650 + 50 * k, 256, 650 + 50 * k, 268, C["ink"], 2)
    s.text(650 + 25 * k, 286, "50 mm on this drawing", size=12, fill=C["muted"], anchor="middle")
    s.text(650, 222, "Always measure with a ruler —", size=12, fill=C["muted"])
    s.text(650, 238, "don't trace a printout", size=12, fill=C["muted"])
    s.save("templates.svg", "Cutting templates with dimensions for every part")


# ============================================================ 7. reel ratio ===
def reel_ratio():
    s = SVG(900, 330)
    s.bg()
    s.rect(420, 262, 460, 14, fill=C["wood"], stroke=C["woodedge"])
    wx, wy, wr = 640, 202, 60
    rx, ry, rr = 190, 150, 100
    s.line(rx, ry - 20, wx, wy - 20, C["reel"], 3, dash="8 5")
    s.line(rx, ry + 20, wx, wy + 20, C["reel"], 3, dash="8 5")
    s.circle(wx, wy, wr, fill=C["tyre"])
    s.circle(wx, wy, wr * 0.74, fill=C["cap"], op=0.9)
    s.circle(wx, wy, 20, fill=C["foam"], stroke=C["reel"], sw=4)
    reel_wheel(s, rx, ry, rr, paddle=20, sw=4, pw=10, start=30)
    s.circle(rx, ry, 20, fill=C["foam"], stroke=C["reel"], sw=4)
    s.line(rx + 70, ry + rr + 22, rx + 180, ry + rr + 22, C["reel"], 3.5, end=True)
    s.text(rx + 70, ry + rr + 48, "paddle tip ≈ 1.7 × ground speed", size=13.5, weight=700, fill=C["reel"])
    s.line(wx - 30, 300, wx - 95, 300, C["ink"], 3.5, end=True)
    s.text(wx - 20, 305, "machine moves this way", size=13.5, weight=700)
    s.line(wx, wy, wx + wr * math.cos(math.radians(-40)), wy + wr * math.sin(math.radians(-40)), "#FFFFFF", 2)
    s.text(wx + 72, wy - 56, "wheel radius 15 mm", size=13, weight=700)
    s.line(rx, ry, rx - 70, ry - 70, C["ink"], 1.3, end=True)
    s.text(rx - 100, ry - 82, "reel radius 25 mm", size=13, weight=700)
    s.text(400, 250, "equal pulleys: reel and wheels turn at the same rate", size=12, fill=C["muted"],
           anchor="middle")
    s.rect(560, 30, 320, 88, fill="#FFFFFF", stroke=C["edge"], rx=8)
    s.text(575, 54, "paddle speed ÷ ground speed", size=13.5, weight=700)
    s.text(575, 76, "= reel radius ÷ wheel radius", size=13.5)
    s.text(575, 98, "= 25 ÷ 15 ≈ 1.7  (real combines: 1.2–1.5)", size=13.5, weight=700, fill=C["tankedge"])
    s.save("reel_ratio.svg", "Ground-driven reel: pulley and belt ratio")


# ======================================================= 8. mod: cut height ===
def mod_height():
    s = SVG(900, 330)
    s.bg()
    s.rect(40, 250, 820, 20, fill=C["bed"], stroke=C["bededge"])
    for x in range(400, 540, 12):
        s.line(x, 250, x, 214, C["green"], 2.2)
    s.rect(430, 40, 300, 120, fill=C["foam"], stroke=C["foamedge"])
    s.text(580, 62, "chassis side plate", size=12.5, fill=C["muted"], anchor="middle")
    for col, hx in enumerate((470, 510)):
        for row, hy in enumerate((92, 112, 132)):
            s.circle(hx, hy, 5, fill=C["bg"], stroke=C["foamedge"])
    for hy, name in ((92, "high · 20 mm"), (112, "mid · 15 mm"), (132, "low · 10 mm")):
        s.text(530, hy + 4, name, size=12, weight=600)
    s.line(520, 112, 300, 204, C["metaledge"], 12)
    s.line(520, 112, 300, 204, "#FFFFFF", 7)
    s.line(470, 112, 520, 112, C["metaledge"], 12)
    s.line(470, 112, 520, 112, "#FFFFFF", 7)
    for hx in (470, 510):
        s.circle(hx, 112, 6, fill=C["brass"], stroke=C["brassedge"], sw=1.5)
    s.poly([(310, 206), (310, 216), (262, 216), (236, 211), (262, 206)], C["guard"], C["guardedge"])
    s.poly([(306, 200), (306, 206), (258, 206), (244, 203), (258, 200)], C["knife"], C["knifedge"])
    s.rect(250, 216, 70, 34, fill=C["wood"], stroke=C["woodedge"])
    s.text(285, 238, "gauge", size=11.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.line(350, 216, 350, 250, C["ink"], 1.3, start=True, end=True)
    s.text(358, 238, "15 mm", size=12.5, weight=700)
    for x in range(52, 240, 12):
        s.cress(x, 250, x + 3, 150, scale=0.9)
    s.rect(560, 172, 310, 120, fill="#FFFFFF", stroke=C["edge"], rx=8)
    s.badge(582, 196, 1, C["ink"])
    s.text(602, 201, "Stand the gauge block on the bed", size=13.5)
    s.badge(582, 228, 2, C["ink"])
    s.text(602, 233, "Rest the knife on it", size=13.5)
    s.badge(582, 260, 3, C["ink"])
    s.text(602, 265, "Pin both holes in the row", size=13.5)
    s.text(602, 283, "that lines up — both sides", size=13.5)
    s.text(40, 312, "Small cress (day 5): 10 mm  ·  Normal: 15 mm  ·  Lumpy bed or knife scraping: 20 mm",
           size=13, fill=C["muted"])
    s.save("mod_height.svg", "Modification: adjustable cutting height")


# ======================================================== 9. mod: speed dial ===
def mod_speed():
    s = SVG(900, 280)
    s.bg()

    def block(x, y, w, h, title, sub, fill, fg="#FFFFFF"):
        s.rect(x, y, w, h, fill=fill, rx=8)
        s.text(x + w / 2, y + h / 2 - 2, title, size=14, weight=700, fill=fg, anchor="middle")
        s.text(x + w / 2, y + h / 2 + 16, sub, size=11.5, fill=fg, anchor="middle")

    block(30, 90, 120, 70, "Battery", "4 × AA · 6 V", C["battery"])
    block(185, 90, 140, 70, "Fuse + switch", "as before", C["grey"], C["ink"])
    s.rect(360, 70, 190, 110, fill=C["pcb"], rx=8)
    s.circle(455, 112, 22, fill="#1E3A8A", stroke="#93C5FD", sw=2)
    s.line(455, 112, 455, 94, "#FFFFFF", 3)
    s.text(455, 155, "PWM speed module", size=13.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(455, 171, "(works at 6 V, ≥ 1 A)", size=11.5, fill="#D1FAE5", anchor="middle")
    for i, t in enumerate(("IN+", "IN−")):
        s.text(372, 94 + 16 * i, t, size=10, weight=700, fill="#D1FAE5")
    for i, t in enumerate(("OUT+", "OUT−")):
        s.text(540, 94 + 16 * i, t, size=10, weight=700, fill="#D1FAE5", anchor="end")
    block(585, 90, 115, 70, "Hold button", "in OUT+", C["knife"])
    s.rect(735, 95, 135, 60, fill=C["metal"], stroke=C["metaledge"], rx=6)
    s.text(802, 124, "N20 cutter", size=14, weight=700, anchor="middle")
    s.text(802, 141, "motor", size=12, anchor="middle")
    for x1, x2 in ((150, 185), (325, 360), (550, 585), (700, 735)):
        s.line(x1, 125, x2 - 4, 125, C["red"], 4, end=True)
    s.path("M802,155 L802,210 L90,210 L90,160", C["black"], 3)
    s.text(450, 232, "black (−) wires join back to the battery through the module's IN− / OUT−",
           size=12.5, fill=C["muted"], anchor="middle")
    s.text(450, 44, "Turn the knob to find the slowest knife speed that still cuts cleanly", size=13.5, weight=700,
           anchor="middle")
    s.save("mod_speed.svg", "Modification: speed-control dial wiring")


# ======================================================= 10. mod: self-drive ===
def mod_drive():
    s = SVG(900, 380)
    s.bg()
    s.text(30, 36, "Side view — rear axle driven by a second, very slow N20", size=15, weight=700)
    s.line(330, 76, 200, 76, C["ink"], 3, end=True)
    s.text(340, 81, "about 24 mm a second", size=13, weight=600)
    s.rect(30, 250, 520, 14, fill=C["wood"], stroke=C["woodedge"])
    s.rect(30, 190, 30, 60, fill=C["woodedge"])
    s.text(45, 180, "end block", size=12, weight=700, anchor="middle")
    s.rect(180, 120, 260, 80, fill=C["foam"], stroke=C["foamedge"])
    wheel(s, 250, 205)
    wheel(s, 390, 205)
    s.rect(394, 199, 24, 12, fill="#7DD3FC", stroke="#0284C7", rx=3, op=0.9)
    # motor faces the axle: drawn mirrored, gearbox and shaft pointing left
    k = 0.9
    s.rect(418, 189, 26 * k, 32 * k, fill=C["brass"], stroke=C["brassedge"])
    s.rect(441, 191, 40 * k, 28 * k, fill=C["metal"], stroke=C["metaledge"], rx=3)
    s.rect(477, 193, 6 * k, 24 * k, fill="#444")
    s.text(470, 112, "N20 · 6 V · 15 RPM", size=12.5, weight=700, anchor="middle")
    s.leader(470, 118, 455, 190)
    s.text(406, 290, "silicone-tube coupler", size=11.5, fill=C["muted"], anchor="middle")
    s.leader(406, 278, 406, 212)
    s.rect(120, 176, 44, 26, fill=C["battery"], rx=3)
    s.line(122, 196, 70, 210, "#9CA3AF", 3)
    s.circle(68, 210, 5, fill="#CBD5E1")
    s.line(164, 188, 182, 168, C["foamedge"], 3)
    s.text(142, 146, "microswitch", size=12, weight=700, anchor="middle")
    s.text(142, 160, "end-stop", size=12, weight=700, anchor="middle")
    s.text(30, 330, "When the lever hits the end block the switch opens", size=13, fill=C["muted"])
    s.text(30, 348, "and BOTH motors stop — even if the button is still held.", size=13, fill=C["muted"])
    s.rect(580, 60, 300, 300, fill="#FFFFFF", stroke=C["edge"], rx=10)
    s.text(730, 84, "Wiring (red + path)", size=14, weight=700, anchor="middle")
    steps = (("Battery +", C["battery"]), ("500 mA fuse", "#FFD166"), ("ON/OFF switch", C["grey"]),
             ("End-stop (C → NC)", "#374151"), ("Hold-to-run button", C["knife"]))
    for i, (t, col) in enumerate(steps):
        y = 100 + 38 * i
        s.rect(620, y, 220, 26, fill=col, rx=5)
        s.text(730, y + 18, t, size=12.5, weight=700, anchor="middle",
               fill=C["ink"] if col in (C["grey"], "#FFD166") else "#FFFFFF")
        if i < 4:
            s.line(730, y + 27, 730, y + 36, C["red"], 2.5, end=True)
    s.path("M730,278 L730,284 M660,292 L660,284 L800,284 L800,292", C["red"], 2.5)
    s.rect(600, 294, 120, 40, fill=C["metal"], stroke=C["metaledge"], rx=5)
    s.text(660, 319, "cutter N20", size=12.5, weight=700, anchor="middle")
    s.rect(740, 294, 120, 40, fill=C["metal"], stroke=C["metaledge"], rx=5)
    s.text(800, 319, "drive N20", size=12.5, weight=700, anchor="middle")
    s.text(730, 352, "motors side by side (in parallel)", size=11.5, fill=C["muted"], anchor="middle")
    s.save("mod_drive.svg", "Modification: self-propelled drive with an automatic end-of-row stop")


# ============================================================= 11. growing ===
def growing():
    s = SVG(900, 300)
    s.bg()
    stages = (("Day 0", "sprinkle seeds on", "damp paper"), ("Day 1", "seeds swell,", "jelly coat"),
              ("Day 2", "tiny white roots", "cover: keep dark"), ("Day 3", "hooks up, pale", "move to window"),
              ("Day 5", "green, 30 mm", "turn tray daily"), ("Day 7", "50–60 mm", "HARVEST!"))
    random.seed(11)
    s.rect(40, 60, 290, 8, fill="#374151", rx=4)
    s.text(185, 50, "dark + damp (cover with a plate)", size=12.5, weight=700, anchor="middle")
    s.rect(330, 60, 530, 8, fill=C["ramp"], rx=4)
    s.text(595, 50, "bright windowsill, keep the paper damp", size=12.5, weight=700, anchor="middle")
    for i, (d, a, b) in enumerate(stages):
        cx = 100 + 140 * i
        s.rect(cx - 55, 196, 110, 18, fill=C["bed"], stroke=C["bededge"])
        for j in range(7):
            x = cx - 42 + j * 14
            if i == 0:
                s.circle(x, 194, 2.8, fill="#8B4513")
            elif i == 1:
                s.circle(x, 193, 5, fill="#E0F2F1", op=0.9)
                s.circle(x, 193, 3.2, fill="#8B4513")
            elif i == 2:
                s.circle(x, 193, 3, fill="#8B4513")
                s.path(f"M{x},{193} q4,-6 2,-12", "#F5F5F4", 2.2)
                s.path(f"M{x},{195} q-3,6 1,10", "#F5F5F4", 1.6)
            elif i == 3:
                s.path(f"M{x},{196} q-2,-14 4,-18 q5,-2 4,4", "#C7D98A", 2.2)
            else:
                h = 58 if i == 4 else 102
                s.cress(x, 196, x + random.uniform(-3, 3), 196 - h, scale=0.8)
        s.text(cx, 240, d, size=15, weight=700, anchor="middle", fill=C["tankedge"] if i == 5 else C["ink"])
        s.text(cx, 258, a, size=12, fill=C["muted"], anchor="middle")
        s.text(cx, 274, b, size=12, fill=C["muted"] if i < 5 else C["knifedge"], anchor="middle")
    s.save("growing.svg", "Growing cress: day-by-day timeline")


# ======================================================= 12. combine compare ===
def compare():
    s = SVG(900, 400)
    s.bg()
    s.text(250, 38, "Real combine harvester (about 10 m long)", size=15, weight=700, anchor="middle")
    s.text(700, 38, "Cress combine (about 24 cm long)", size=15, weight=700, anchor="middle")
    s.line(30, 290, 480, 290, "#8B6F47", 3)
    for x in range(40, 90, 9):
        s.line(x, 290, x, 212, "#C9A227", 2.2)
    for x in range(160, 470, 9):
        s.line(x, 290, x, 278, "#C9A227", 2)
    s.poly([(200, 150), (420, 150), (440, 250), (190, 250)], "#E9C46A", "#B08D2E")
    s.rect(280, 90, 110, 60, fill=C["tank"], stroke=C["tankedge"])
    s.rect(210, 95, 60, 55, fill="#A8DADC", stroke="#457B9D")
    s.path("M390,110 L470,70", C["grey"], 9)
    s.circle(320, 205, 26, fill=C["grey"], stroke="#4B5563", sw=2)
    s.poly([(120, 262), (205, 200), (215, 216), (135, 276)], C["ramp"], C["rampedge"])
    s.poly([(150, 275), (150, 282), (95, 282), (80, 278), (95, 275)], C["knife"], C["knifedge"])
    s.circle(115, 225, 30, stroke=C["reel"], sw=5)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang + 20)
        s.line(115, 225, 115 + 30 * math.cos(a), 225 + 30 * math.sin(a), C["reel"], 3)
    s.rect(370, 170, 50, 40, fill=C["brass"], stroke=C["brassedge"])
    wheel(s, 250, 256, 34)
    wheel(s, 405, 270, 20)
    s.line(520, 290, 880, 290, "#8B6F47", 3)
    for x in range(530, 590, 8):
        s.line(x, 290, x, 225, C["green"], 2)
    for x in range(630, 870, 8):
        s.line(x, 290, x, 278, C["green"], 2)
    s.rect(700, 196, 160, 50, fill=C["foam"], stroke=C["foamedge"])
    s.rect(730, 164, 90, 32, fill=C["battery"], rx=3)
    s.poly([(640, 262), (640, 280), (695, 280), (695, 244)], C["tank"], C["tankedge"])
    s.poly([(612, 280), (616, 285), (642, 272), (638, 267)], C["ramp"], C["rampedge"])
    s.poly([(618, 279), (618, 285), (592, 285), (582, 282), (592, 279)], C["knife"], C["knifedge"])
    s.circle(590, 240, 22, stroke=C["reel"], sw=4)
    s.rect(606, 238, 14, 30, fill=C["brass"], stroke=C["brassedge"])
    wheel(s, 730, 268, 22)
    wheel(s, 835, 268, 22)
    items = ((C["reel"], "Reel", "same job in both"), (C["knife"], "Cutter bar", "same scissor action"),
             (C["ramp"], "Feeder / ramp", "carries the crop back"),
             (C["tank"], "Grain / cress tank", "stores the harvest"),
             (C["brass"], "Engine / N20 motor", "hundreds of hp vs about 1 W"),
             (C["grey"], "Threshing drum", "not needed — we eat the leaves!"))
    for i, (col, t, sub) in enumerate(items):
        x = 40 + 285 * (i % 3)
        y = 330 + 36 * (i // 3)
        s.rect(x, y - 12, 18, 14, fill=col, rx=3)
        s.text(x + 26, y, t, size=13.5, weight=700)
        s.text(x + 26, y + 15, sub, size=11.5, fill=C["muted"])
    s.save("compare.svg", "Real combine harvester compared with the cress combine, colour-matched parts")


# ================================================= Part 7: Korody RC conversion ===
# The toy is drawn as a plain schematic shape: its insides are unknown, so the
# figures show where things go, not the toy's real internals.
TOY, TOYEDGE = "#43A047", "#2E7D32"


def toy_wheel(s, cx, cy, r):
    s.circle(cx, cy, r, fill="#222")
    s.circle(cx, cy, r * 0.55, fill="#FBC02D", stroke="#B8860B", sw=1.5)
    s.circle(cx, cy, 4, fill="#333")


def korody_overview():
    s = SVG(900, 480)
    s.bg()
    random.seed(21)
    s.rect(30, 332, 840, 52, fill=C["tub"], stroke=C["tubedge"], rx=3)
    s.rect(34, 356, 832, 22, fill=C["bed"], stroke=C["bededge"])
    for x in range(44, 150, 11):
        s.cress(x, 356, x + random.uniform(-5, 5), 356 - random.uniform(130, 150))
    for x in range(152, 178, 8):
        s.cress(x, 356, x + 26, 356 - random.uniform(100, 112))
    for x in range(186, 866, 11):
        s.line(x, 356, x + random.uniform(-1, 1), 318 + random.uniform(-2, 2), C["green"], 2.2)
    s.rect(30, 330, 840, 13, fill="#E5E7EB", stroke=C["foamedge"], op=0.92)
    s.text(470, 340.5, "tramline: the foam-board track the tyres run on", size=10.5, weight=600)
    s.rect(30, 384, 840, 12, fill="#D1D5DB", stroke=C["foamedge"])
    s.text(46, 410, "sunken tray between the tramlines · cress bed (15 − H) mm below the tramline top", size=12,
           fill=C["muted"])
    # the RC combine, as a simple shape
    s.poly([(300, 250), (300, 150), (770, 150), (800, 250)], TOY, TOYEDGE, 2)
    s.rect(300, 62, 115, 88, fill="#A8DADC", stroke=TOYEDGE, sw=3, rx=4)
    s.rect(296, 56, 123, 10, fill=TOY, stroke=TOYEDGE, rx=3)
    s.circle(357, 50, 6, fill=C["ramp"])
    s.rect(470, 104, 210, 46, fill="#388E3C", stroke=TOYEDGE, sw=2)
    s.path("M660,112 L790,58", C["grey"], 9)
    s.poly([(300, 170), (300, 250), (250, 272), (242, 252)], TOY, TOYEDGE, 2)
    s.rect(560, 156, 64, 40, fill="none", stroke="#FFFFFF", sw=1.5, dash="4 3")
    s.text(592, 173, "circuit", size=10.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(592, 186, "board", size=10.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.rect(650, 156, 64, 40, fill="none", stroke="#FFFFFF", sw=1.5, dash="4 3")
    s.text(682, 173, "drive", size=10.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(682, 186, "motor", size=10.5, weight=700, fill="#FFFFFF", anchor="middle")
    s.path("M682,196 L682,210", "#FFFFFF", 1.5, dash="3 3")
    s.rect(462, 190, 80, 42, fill="#FFFFFF", stroke=C["ink"], rx=4)
    s.text(502, 207, "fuse · diode", size=10.5, weight=700, anchor="middle")
    s.text(502, 222, "· switch", size=10.5, weight=700, anchor="middle")
    s.path("M650,206 L542,206", C["red"], 2.4)
    s.path("M650,214 L542,214", C["black"], 2.4)
    s.path("M462,206 C400,206 320,200 272,232", C["red"], 2.4)
    s.path("M462,214 C404,214 326,210 272,240", C["black"], 2.4)
    s.rect(252, 226, 20, 18, fill="#FFFFFF", stroke=C["ink"], sw=1.5)
    s.path("M252,232 C240,230 228,226 218,222", C["red"], 2.2)
    s.path("M252,238 C240,238 232,232 226,222", C["black"], 2.2)
    toy_wheel(s, 365, 272, 58)
    toy_wheel(s, 730, 294, 36)
    # new header on the toy's head mount
    s.line(246, 262, 206, 300, C["metaledge"], 9)
    s.line(246, 262, 206, 300, "#FFFFFF", 4.5)
    s.circle(246, 262, 5, fill="#555")
    s.poly([(252, 302), (252, 318), (304, 318), (304, 286)], C["tank"], C["tankedge"], 1.5)
    s.rect(150, 300, 110, 6, fill=C["foam"], stroke=C["foamedge"], sw=1.2)
    n20(s, 205, 224)
    s.ellipse(218, 303, 15, 4, C["crank"], stroke=C["crankedge"])
    s.poly([(250, 314), (250, 322), (180, 322), (150, 318), (180, 314)], C["guard"], C["guardedge"], 1.2)
    s.poly([(246, 309), (246, 314), (178, 314), (160, 311.5), (178, 309)], C["knife"], C["knifedge"], 1.2)
    # labels
    s.line(210, 34, 44, 34, C["ink"], 3, end=True)
    s.text(222, 39, "drive forward: the knife runs · reverse or stop: it doesn't", size=14, weight=600)
    s.label(490, 80, "Your RC combine", "drawn as a simple shape", TOY)
    s.label(40, 446, "N20 (3 V)", "runs only when driving", C["brass"])
    s.leader(90, 430, 206, 262)
    s.label(200, 446, "Cutter bar", "same scissor knife", C["knife"])
    s.leader(240, 430, 200, 320)
    s.label(360, 446, "JST plug", "header unplugs", "#FFFFFF")
    s.leader(380, 430, 262, 244)
    s.label(500, 446, "Tap circuit", "on the drive-motor wires", C["red"])
    s.leader(520, 430, 502, 232)
    s.label(700, 446, "Catch tank", "right behind the knife", C["tank"])
    s.leader(710, 430, 290, 312)
    s.save("korody_overview.svg", "Korody RC combine converted with an N20 cutter header and drive-motor tap")


def korody_wiring():
    s = SVG(900, 460)
    s.bg()
    s.rect(30, 250, 120, 76, fill=C["battery"], rx=6)
    s.text(90, 282, "3.7 V", size=15, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(90, 300, "Li-ion (14500)", size=11, fill="#D1D5DB", anchor="middle")
    s.text(90, 344, "toy's battery", size=12, fill=C["muted"], anchor="middle")
    s.rect(200, 220, 170, 130, fill=C["pcb"], rx=8)
    s.rect(250, 266, 64, 40, fill="#111111", rx=3)
    s.text(282, 291, "driver", size=11, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(285, 244, "toy's circuit board", size=12, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(285, 334, "radio + motor driver", size=11, fill="#D1FAE5", anchor="middle")
    s.path("M150,270 L200,270", C["red"], 4)
    s.path("M150,306 L200,306", C["black"], 4)
    # drive motor
    s.rect(690, 272, 14, 60, fill="#444")
    s.rect(704, 266, 120, 72, fill=C["metal"], stroke=C["metaledge"], rx=6)
    s.line(824, 302, 860, 302, "#555", 5, cap="butt")
    s.text(764, 362, "toy's drive motor", size=13, weight=700, anchor="middle")
    # motor wires, optional field-mode resistor on wire A
    s.path("M370,262 L530,262", C["red"], 4)
    s.path("M600,262 L660,262 L660,290 L694,290", C["red"], 4)
    s.path("M370,320 L660,320 L660,314 L694,314", C["black"], 4)
    s.rect(500, 206, 134, 76, fill="none", stroke=C["muted"], sw=1.3, dash="5 4", rx=6)
    s.text(567, 200, "optional field mode", size=11, weight=700, fill=C["muted"], anchor="middle")
    s.rect(530, 254, 70, 16, fill="#E9D8A6", stroke="#8A6D3B", rx=5)
    for x, col in ((545, "#D62828"), (555, "#D62828"), (578, "#C9A227"), (588, "#C9A227")):
        s.line(x, 255, x, 269, col, 3, cap="butt")
    s.path("M515,262 L515,230 L548,230", C["muted"], 2)
    s.line(548, 230, 578, 220, C["muted"], 2.5)
    s.path("M586,230 L618,230 L618,262", C["muted"], 2)
    s.text(567, 296, "2.2 Ω 2 W + bypass switch", size=10.5, fill=C["muted"], anchor="middle")
    s.text(380, 252, "wire A", size=11.5, weight=700, fill=C["red"])
    s.text(380, 340, "wire B", size=11.5, weight=700)
    # tap chain
    s.circle(430, 262, 5, fill=C["red"])
    s.circle(455, 320, 5, fill=C["black"])
    s.path("M430,262 L430,110 L464,110", C["red"], 3.5)
    s.circle(482, 110, 18, fill="#FFD166", stroke="#C99A2E", sw=2)
    s.text(482, 114, "PTC", size=9.5, weight=700, anchor="middle")
    s.path("M500,110 L540,110", C["red"], 3.5)
    s.rect(540, 100, 64, 20, fill="#111111", rx=3)
    s.rect(592, 100, 7, 20, fill="#D1D5DB")
    s.text(564, 114, "1N5819", size=9, weight=700, fill="#FFFFFF", anchor="middle")
    s.path("M604,110 L640,110", C["red"], 3.5)
    s.rect(640, 94, 64, 32, fill=C["grey"], stroke=C["metaledge"], rx=4)
    s.rect(648, 102, 48, 16, fill="#4B5563", rx=2)
    s.rect(674, 104, 20, 12, fill="#E5E7EB", rx=2)
    s.path("M704,110 L716,110", C["red"], 3.5)
    s.rect(716, 94, 22, 96, fill="#FFFFFF", stroke=C["ink"], sw=1.5)
    s.rect(740, 94, 22, 96, fill="#F5F5F4", stroke=C["ink"], sw=1.5)
    s.path("M762,110 L780,110 L780,145 L803,145", C["red"], 3)
    s.path("M803,160 L780,160 L780,172 L762,172", C["black"], 3)
    s.path("M716,172 L455,172 L455,320", C["black"], 3.5)
    s.line(770, 145, 770, 160, "#777", 1.5)
    s.circle(770, 152, 6.5, fill="#E09F3E", stroke="#9A6A1F")
    n20(s, 800, 139, horizontal=True, scale=0.9)
    s.text(470, 72, "300 mA fuse", size=12.5, weight=700, anchor="middle")
    s.text(572, 40, "Schottky diode", size=12.5, weight=700, anchor="middle")
    s.text(572, 56, "stripe towards the N20", size=11, fill=C["muted"], anchor="middle")
    s.text(672, 80, "cutter ON/OFF", size=12.5, weight=700, anchor="middle")
    s.text(739, 208, "JST plug", size=12.5, weight=700, anchor="middle")
    s.text(739, 223, "header unplugs", size=11, fill=C["muted"], anchor="middle")
    s.text(840, 128, "N20 · 3 V", size=12.5, weight=700, anchor="middle")
    s.text(840, 186, "+ 100 nF", size=11, fill=C["muted"], anchor="middle")
    s.text(560, 166, "black back to wire B", size=11, fill=C["muted"], anchor="middle")
    s.rect(30, 380, 410, 64, fill="#FFFFFF", stroke=C["edge"], rx=8)
    s.text(46, 404, "FORWARD: wire A is + → diode conducts → knife cuts", size=13, weight=700, fill=C["green"])
    s.text(46, 426, "Let go of the stick → no power → wheels and knife stop.", size=12, fill=C["muted"])
    s.rect(460, 380, 410, 64, fill="#FFFFFF", stroke=C["edge"], rx=8)
    s.text(476, 404, "REVERSE: polarity flips → diode blocks → no cutting", size=13, weight=700, fill=C["knifedge"])
    s.text(476, 426, "Cutter switch OFF → drive around without cutting.", size=12, fill=C["muted"])
    s.save("korody_wiring.svg", "Wiring the N20 cutter to the RC combine's drive motor through a fuse, diode and switch")


def korody_field():
    s = SVG(900, 400)
    s.bg()
    s.rect(140, 30, 620, 76, fill=TOY, stroke=TOYEDGE, op=0.22, rx=10)
    s.text(450, 74, "your combine, seen from the front", size=13, weight=700, fill=TOYEDGE, anchor="middle")
    s.rect(40, 290, 820, 20, fill="#D1D5DB", stroke=C["foamedge"])
    for x0, x1 in ((60, 285), (615, 840)):
        s.rect(x0, 200, x1 - x0, 90, fill="#F3F4F6", stroke=C["foamedge"])
        for yy in (230, 260):
            s.line(x0, yy, x1, yy, C["foamedge"], 0.8, dash="3 3")
    s.text(172, 250, "tramline", size=12.5, weight=700, anchor="middle")
    s.text(172, 268, "stacked foam board", size=11, fill=C["muted"], anchor="middle")
    s.text(728, 250, "tramline", size=12.5, weight=700, anchor="middle")
    for kx in (110, 238, 662, 790):
        s.rect(kx, 186, 8, 14, fill=C["wood"], stroke=C["woodedge"], sw=1)
    for tx in (125, 675):
        s.rect(tx, 116, 100, 84, fill="#222222", rx=10)
    s.text(175, 162, "tyre", size=12, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(725, 162, "tyre", size=12, weight=700, fill="#FFFFFF", anchor="middle")
    s.rect(285, 200, 330, 90, fill=C["tub"], stroke=C["tubedge"], sw=2)
    s.rect(291, 230, 318, 56, fill=C["bed"], stroke=C["bededge"])
    for x in range(300, 604, 10):
        s.line(x, 230, x, 186, C["green"], 2)
    s.rect(262, 178, 376, 7, fill=C["knife"], stroke=C["knifedge"], sw=1)
    s.rect(262, 185, 376, 6, fill=C["guard"], stroke=C["guardedge"], sw=1)
    s.text(450, 172, "knife", size=11.5, weight=700, fill=C["knifedge"], anchor="middle")
    s.line(250, 186, 250, 200, C["ink"], 1.3, start=True, end=True)
    s.text(242, 197, "H", size=13, weight=700, anchor="end")
    s.line(650, 186, 650, 230, C["ink"], 1.3, start=True, end=True)
    s.text(660, 212, "15 mm cut", size=11.5, weight=700)
    s.line(225, 112, 675, 112, C["ink"], 1.3, start=True, end=True)
    s.text(450, 126, "gap between the tyres (measure it)", size=12, weight=700, anchor="middle")
    s.line(285, 326, 615, 326, C["ink"], 1.3, start=True, end=True)
    s.text(450, 344, "tray width ≤ tyre gap − 20 mm", size=12.5, weight=700, anchor="middle")
    s.text(450, 372, "bed depth below the tramline top = 15 mm − H   ·   kerbs (lolly sticks) keep the tyres on track",
           size=12.5, fill=C["muted"], anchor="middle")
    s.save("korody_field.svg", "Front view of the field: tramlines, sunken tray and cutting height")


def korody_polarity():
    s = SVG(900, 280)
    s.bg()
    panels = ((True, "Press FORWARD — the LED lights", "the wire on the LED's long leg is wire A (+)"),
              (False, "LED stays dark?", "swap the two clips and press forward again"))
    for k, (lit, title, sub) in enumerate(panels):
        ox = 20 + 440 * k
        s.rect(ox, 20, 420, 240, fill="#FFFFFF", stroke=C["edge"], rx=10)
        s.text(ox + 210, 44, "LED + 100 Ω resistor across the motor terminals", size=12, fill=C["muted"],
               anchor="middle")
        s.rect(ox + 300, 90, 12, 56, fill="#444")
        s.rect(ox + 312, 84, 90, 68, fill=C["metal"], stroke=C["metaledge"], rx=5)
        s.text(ox + 357, 172, "drive motor", size=12, weight=700, anchor="middle")
        lx, ly = ox + 80, 130
        if lit:
            for a in range(0, 360, 45):
                r = math.radians(a)
                s.line(lx + 28 * math.cos(r), ly + 28 * math.sin(r), lx + 38 * math.cos(r), ly + 38 * math.sin(r),
                       "#F59E0B", 2.5)
        s.circle(lx, ly, 20, fill=C["knife"] if lit else "#F6D5D8", stroke=C["knifedge"], sw=2)
        long_col, short_col = (C["red"], C["black"]) if k == 0 else (C["black"], C["red"])
        s.path(f"M{lx + 6},{ly - 18} L{lx + 6},{ly - 50} L{ox + 150},{ly - 50}", "#777", 2)
        s.rect(ox + 150, ly - 57, 46, 14, fill="#E9D8A6", stroke="#8A6D3B", rx=4)
        s.text(ox + 173, ly - 64, "100 Ω", size=11, weight=700, anchor="middle")
        s.path(f"M{ox + 196},{ly - 50} L{ox + 250},{ly - 50} L{ox + 250},{102} L{ox + 300},{102}", long_col, 3)
        s.path(f"M{lx - 6},{ly + 18} L{lx - 6},{ly + 40} L{ox + 250},{ly + 40} L{ox + 250},{134} L{ox + 300},{134}",
               short_col, 3)
        s.text(lx + 14, ly - 30, "long leg", size=10.5, fill=C["muted"])
        s.text(lx + 2, ly + 56, "short leg", size=10.5, fill=C["muted"])
        s.text(ox + 272, 96, "A", size=12, weight=700, fill=C["red"])
        s.text(ox + 272, 150, "B", size=12, weight=700)
        s.text(ox + 210, 214, title, size=15, weight=700, anchor="middle", fill=C["green"] if lit else C["ink"])
        s.text(ox + 210, 236, sub, size=12.5, fill=C["muted"], anchor="middle")
    s.save("korody_polarity.svg", "Finding which drive-motor wire is positive in forward with an LED tester")


def korody_header():
    s = SVG(900, 470)
    s.bg()
    s.poly([(700, 150), (860, 120), (860, 300), (700, 270)], TOY, TOYEDGE, 2)
    s.text(790, 206, "toy's feeder", size=12, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(790, 222, "house", size=12, weight=700, fill="#FFFFFF", anchor="middle")
    for (x1, y1, x2, y2, x3, y3) in ((236, 110, 560, 110, 624, 192), (236, 320, 560, 320, 624, 228)):
        s.path(f"M{x1},{y1} L{x2},{y2} L{x3},{y3}", C["metaledge"], 12)
        s.path(f"M{x1},{y1} L{x2},{y2} L{x3},{y3}", "#FFFFFF", 7)
    s.rect(616, 178, 84, 64, fill=C["grey"], stroke=C["metaledge"], rx=4)
    s.circle(700, 210, 7, fill="#555")
    s.rect(236, 92, 120, 236, fill=C["tank"], stroke=C["tankedge"])
    s.text(296, 214, "CATCH", size=13, weight=700, fill="#FFFFFF", anchor="middle")
    s.text(296, 230, "TANK", size=13, weight=700, fill="#FFFFFF", anchor="middle")
    s.rect(206, 80, 30, 340, fill=C["foam"], stroke=C["foamedge"], sw=1.2)
    for i in range(12):
        c = 100 + 20 * i
        s.poly([(206, c - 8), (206, c + 8), (178, c)], C["guard"], C["guardedge"], 1)
        s.poly([(206, c + 2), (206, c + 18), (186, c + 10)], C["knife"], C["knifedge"], 1, op=0.9)
    s.line(221, 334, 219, 400, C["wood"], 7)
    s.circle(229, 402, 15, fill=C["crank"], stroke=C["crankedge"])
    s.circle(219, 402, 3.5, fill=C["brass"], stroke=C["brassedge"], sw=1)
    s.rect(216, 390, 30, 26, fill=C["metal"], stroke=C["metaledge"], op=0.55, rx=2)
    s.rect(586, 296, 26, 16, fill="#FFFFFF", stroke=C["ink"], sw=1.5)
    s.path("M246,408 L596,408 L596,312", C["red"], 2.4)
    s.path("M246,414 L604,414 L604,312", C["black"], 2.4)
    s.path("M612,300 L660,300 L706,262", C["red"], 2)
    s.path("M612,306 L664,306 L710,268", C["black"], 2)
    s.line(150, 92, 150, 328, C["ink"], 1.3, start=True, end=True)
    s.text(140, 210, "cut width 120 mm", size=12.5, weight=700, anchor="middle", rot=-90)
    s.line(90, 80, 90, 420, C["ink"], 1.3, start=True, end=True)
    s.text(80, 250, "mount plate = cut width + 60 mm", size=12.5, weight=700, anchor="middle", rot=-90)
    s.line(420, 40, 250, 40, C["ink"], 3, end=True)
    s.text(432, 45, "direction of travel", size=14, weight=600)
    s.text(420, 446, "N20 (3 V) + crank on the plate, inside the header width", size=12.5, weight=700,
           fill=C["brassedge"])
    s.leader(420, 440, 248, 404)
    s.text(740, 350, "clip part kept from the", size=12.5, weight=700, anchor="middle")
    s.text(740, 366, "spare head (grown-up cuts)", size=12.5, weight=700, anchor="middle")
    s.leader(740, 336, 668, 242)
    s.text(740, 396, "to the tap circuit →", size=12, fill=C["muted"], anchor="middle")
    s.text(740, 420, "coins in the grain tank balance the header", size=12, fill=C["muted"], anchor="middle")
    s.text(600, 290, "JST", size=11, weight=700, anchor="middle")
    s.save("korody_header.svg", "Top view of the new cutter header fitted to the RC combine's head mount")


if __name__ == "__main__":
    for fn in (side_view, plan_view, cutter_mechanism, shear_frames, wiring, templates, reel_ratio,
               mod_height, mod_speed, mod_drive, growing, compare,
               korody_overview, korody_wiring, korody_field, korody_polarity, korody_header):
        fn()
    print("wrote", len([f for f in os.listdir(OUT) if f.endswith(".svg")]), "SVGs")
