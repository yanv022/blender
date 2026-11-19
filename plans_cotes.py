# Plans cotes de la mini-usine bauxite -> alumine : 4 planches SVG au format A3 paysage.
# Les cotes viennent du modele 3D (construire_usine.py). Unites : millimetres.
# Usage : python plans_cotes.py   -> ecrit les planches dans le dossier plans/

import math
import os

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plans")
W, H = 420.0, 297.0                          # A3 paysage


class Planche:
    def __init__(self, numero, titre, echelles):
        self.numero, self.titre, self.echelles = numero, titre, echelles
        self.el = []

    def add(self, s):
        self.el.append(s)

    def line(self, x1, y1, x2, y2, w=0.35, dash=None, col="#000"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" '
                 f'stroke-width="{w}"{d}/>')

    def poly(self, pts, w=0.5, fill="none", close=True, dash=None):
        p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="#000" stroke-width="{w}"{d}/>')

    def circle(self, cx, cy, r, w=0.5, fill="none", dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="#000" '
                 f'stroke-width="{w}"{d}/>')

    def text(self, x, y, s, size=3.0, anchor="middle", rot=0, bold=False, col="#000"):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        b = ' font-weight="bold"' if bold else ""
        r = f' transform="rotate({rot:.1f} {x:.2f} {y:.2f})"' if rot else ""
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-family="Arial, Helvetica, sans-serif" fill="{col}"{b}{r}>{s}</text>')

    def fleche(self, x, y, ang):
        a, l, e = ang, 2.2, 0.7
        p1 = (x - l * math.cos(a) + e * math.sin(a), y - l * math.sin(a) - e * math.cos(a))
        p2 = (x - l * math.cos(a) - e * math.sin(a), y - l * math.sin(a) + e * math.cos(a))
        self.add(f'<polygon points="{x:.2f},{y:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="#000"/>')

    def cadre(self):
        self.add(f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="#000" stroke-width="0.7"/>')
        x0, y0 = W - 10 - 190, H - 10 - 34
        self.add(f'<rect x="{x0}" y="{y0}" width="190" height="34" fill="#fff" stroke="#000" stroke-width="0.5"/>')
        self.line(x0, y0 + 12, x0 + 190, y0 + 12, 0.35)
        self.line(x0 + 120, y0 + 12, x0 + 120, y0 + 34, 0.35)
        self.text(x0 + 95, y0 + 8.5, f"Planche {self.numero}/4 — {self.titre}", 4.6, bold=True)
        self.text(x0 + 4, y0 + 18, "Mini-usine bauxite → alumine (lot de démarrage 5 kg)", 2.8, "start")
        self.text(x0 + 4, y0 + 23.5, "Cotes en mm, tirées du modèle 3D.", 2.8, "start")
        self.text(x0 + 4, y0 + 29, "À vérifier sur les pièces achetées avant toute découpe.", 2.8, "start")
        self.text(x0 + 155, y0 + 19, "Échelles", 2.8)
        self.text(x0 + 155, y0 + 25, self.echelles, 3.0, bold=True)

    def ecrire(self, nom):
        os.makedirs(DOSSIER, exist_ok=True)
        self.cadre()
        defs = ('<defs><pattern id="hachures" width="2" height="2" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2" stroke="#000" '
                'stroke-width="0.25"/></pattern></defs>')
        svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">\n'
               f'<rect width="{W}" height="{H}" fill="#fff"/>\n{defs}\n' + "\n".join(self.el) + "\n</svg>\n")
        chemin = os.path.join(DOSSIER, nom)
        with open(chemin, "w", encoding="utf-8") as fh:
            fh.write(svg)
        return chemin


class Vue:
    """Vue a l'echelle : coordonnees reelles (X a droite, Z en haut, en mm) -> feuille."""

    def __init__(self, P, ox, oy, echelle):
        self.P, self.ox, self.oy, self.s = P, ox, oy, 1.0 / echelle

    def pt(self, X, Z):
        return (self.ox + X * self.s, self.oy - Z * self.s)

    def line(self, X1, Z1, X2, Z2, **k):
        a, b = self.pt(X1, Z1), self.pt(X2, Z2)
        self.P.line(a[0], a[1], b[0], b[1], **k)

    def rect(self, X0, Z0, X1, Z1, w=0.5, fill="none", dash=None):
        self.P.poly([self.pt(X0, Z0), self.pt(X1, Z0), self.pt(X1, Z1), self.pt(X0, Z1)], w, fill, dash=dash)

    def poly(self, pts, w=0.5, fill="none", close=True, dash=None):
        self.P.poly([self.pt(X, Z) for X, Z in pts], w, fill, close, dash)

    def circle(self, X, Z, R, w=0.5, fill="none", dash=None):
        c = self.pt(X, Z)
        self.P.circle(c[0], c[1], R * self.s, w, fill, dash)

    def axe(self, X1, Z1, X2, Z2):
        self.line(X1, Z1, X2, Z2, w=0.2, dash="6,1.5,1,1.5")

    def texte(self, X, Z, s, size=2.8, anchor="middle", rot=0, bold=False):
        p = self.pt(X, Z)
        self.P.text(p[0], p[1], s, size, anchor, rot, bold)

    def cote_h(self, X1, X2, Z, txt=None, Zref=(None, None)):
        """Cote horizontale entre X1 et X2, ligne de cote a la hauteur Z."""
        a, b = self.pt(X1, Z), self.pt(X2, Z)
        for X, Zr in ((X1, Zref[0]), (X2, Zref[1])):
            if Zr is not None:
                p, q = self.pt(X, Zr), self.pt(X, Z)
                self.P.line(p[0], p[1] + (-1 if q[1] < p[1] else 1), q[0], q[1] + (-1.2 if q[1] < p[1] else 1.2), 0.18)
        self.P.line(a[0], a[1], b[0], b[1], 0.18)
        self.P.fleche(a[0], a[1], math.pi)
        self.P.fleche(b[0], b[1], 0)
        self.P.text((a[0] + b[0]) / 2, a[1] - 1.0, txt or f"{abs(X2 - X1):.0f}", 2.6)

    def cote_v(self, Z1, Z2, X, txt=None, Xref=(None, None)):
        """Cote verticale entre Z1 et Z2, ligne de cote a l'abscisse X."""
        a, b = self.pt(X, Z1), self.pt(X, Z2)
        for Z, Xr in ((Z1, Xref[0]), (Z2, Xref[1])):
            if Xr is not None:
                p, q = self.pt(Xr, Z), self.pt(X, Z)
                sgn = 1 if q[0] > p[0] else -1
                self.P.line(p[0] + sgn * 1, p[1], q[0] + sgn * 1.2, q[1], 0.18)
        self.P.line(a[0], a[1], b[0], b[1], 0.18)
        self.P.fleche(a[0], a[1], math.pi / 2)
        self.P.fleche(b[0], b[1], -math.pi / 2)
        self.P.text(a[0] - 1.2, (a[1] + b[1]) / 2, txt or f"{abs(Z2 - Z1):.0f}", 2.6, rot=-90)

    def titre(self, X, Z, s):
        self.texte(X, Z, s, 3.4, bold=True)

    def repere(self, X, Z, Xt, Zt, s, anchor="start"):
        """Ligne de rappel + texte."""
        self.line(X, Z, Xt, Zt, w=0.18)
        p = self.pt(X, Z)
        self.P.circle(p[0], p[1], 0.5, 0.18, "#000")
        self.texte(Xt + (2 if anchor == "start" else -2) / self.s, Zt - 1.0 / self.s, s, 2.6, anchor)


def notes(P, x, y, lignes, size=2.7):
    for i, l in enumerate(lignes):
        P.text(x, y + i * (size + 1.6), l, size, "start", bold=(i == 0))


# ====================================================================== PLANCHE 1 : CUVE R
def planche_cuve():
    P = Planche(1, "Cuve agitée R (×2)", "1:5")
    V = Vue(P, 120, 205, 5)
    V.titre(0, -110, "COUPE VERTICALE (R1 ; R2 symétrique)")
    V.rect(-210, -54, 210, -4, 0.4, "#ddd")
    V.texte(0, -36, "plaque 3 kW 420×420", 2.4)
    # paroi de la marmite (en coupe)
    V.poly([(-200, 0), (200, 0), (200, 400), (197, 400), (197, 6), (-197, 6), (-197, 400), (-200, 400)],
           0.4, "#333")
    V.poly([(-206, 400), (-11, 400), (-11, 403), (-206, 403)], 0.3, "#333")
    V.poly([(11, 400), (206, 400), (206, 403), (11, 403)], 0.3, "#333")
    for s in (-1, 1):                         # isolation + habillage
        V.rect(s * 202, 110, s * 250, 390, 0.3, "url(#hachures)")
        V.rect(s * 250, 105, s * 252, 395, 0.3)
        V.rect(s * 197, 40, s * 162, 340, 0.3)    # chicanes
    V.axe(0, -70, 0, 600)
    V.rect(-7, 60, 7, 548, 0.35)               # arbre D14
    V.rect(-16, 50, 16, 80, 0.4)               # moyeu
    V.poly([(-65, 50), (-16, 80), (-16, 70), (-65, 40)], 0.4)
    V.poly([(65, 80), (16, 50), (16, 60), (65, 90)], 0.4)
    V.line(-197, 205, 197, 205, w=0.25, dash="3,1.5")
    V.texte(30, 212, "niveau ≈ 25 L", 2.4, "start")
    for z in (22, 75):                         # piquages + vannes DN25
        V.rect(200, z - 17, 300, z + 17, 0.35)
        V.circle(335, z, 33, 0.4)
        V.rect(370, z - 17, 410, z + 17, 0.35)
    # cotes
    V.cote_h(-200, 200, 470, "Ø 400 (marmite 50 L)", (403, 403))
    V.cote_h(-252, 252, 520, "Ø 504 avec isolation 50", (395, 395))
    V.cote_v(0, 400, -300, "400", (-200, -200))
    V.cote_v(110, 390, -275, "280", (-252, -252))
    V.cote_v(0, 22, 450, "22", (410, 410))
    V.cote_v(0, 75, 480, "75", (410, 410))
    V.cote_h(-65, 65, 120, "turbine Ø 130")
    V.cote_v(0, 65, 95, "65", (16, 16))
    V.cote_v(40, 340, -130, "chicanes 300", (-162, -162))
    V.repere(0, 300, 40, 340, "arbre inox Ø 14")
    V.repere(335, 75, 380, 160, "vannes DN25 à boisseau, passage intégral")
    V.repere(226, 250, 300, 300, "laine de roche 50 + tôle inox")

    T = Vue(P, 335, 110, 5)
    T.titre(0, -280, "COUVERCLE (vue de dessus, R1)")
    T.circle(0, 0, 206, 0.5)
    T.circle(0, 0, 11, 0.4)
    T.axe(-230, 0, 230, 0)
    T.axe(0, -230, 0, 230)
    pos = {"trappe": (125, -15, 38), "doigt": (140, 180, 5), "event": (130, 150, 12.5)}
    for nom, (r, a, rr) in pos.items():
        x, y = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        T.circle(x, y, rr, 0.45)
        T.axe(0, 0, x * 1.15, y * 1.15)
    T.circle(125 * math.cos(math.radians(-15)), 125 * math.sin(math.radians(-15)), 46, 0.25, dash="2,1")
    for a in (15, -15):                         # directions des vannes
        T.line(206 * math.cos(math.radians(a)), 206 * math.sin(math.radians(a)),
               260 * math.cos(math.radians(a)), 260 * math.sin(math.radians(a)), w=0.35)
    T.texte(150, -130, "trappe Ø 76 (collerette Ø 92)", 2.5, "start")
    T.texte(150, -150, "à R 125, à −15°", 2.5, "start")
    T.texte(-215, 12, "doigt de gant Ø 10 à R 140, 180°", 2.5, "end")
    T.texte(-190, 120, "évent Ø 25 à R 130, 150°", 2.5, "end")
    T.texte(268, 75, "vannes à ±15°", 2.5, "start")
    T.texte(0, 22, "arbre Ø 22", 2.4)
    T.cote_h(-206, 206, 245, "Ø 412", (0, 0))
    notes(P, 245, 205, [
        "NOTES",
        "• Marmite inox 304/316, fond sandwich ; couvercle inox 3 mm.",
        "• Trappe : trou Ø 76, collerette inox Ø 76×30 soudée TIG,",
        "  couvercle Ø 100 à charnière côté extérieur + bouton.",
        "• Vannes : manchons 1\" inox soudés TIG, joints PTFE.",
        "• Chicanes 35×300 à 90°, 200° et 340°.",
        "• R2 : identique, symétrique (trappe à 195°).",
        "• Volume utile 18–35 L ; évent toujours ouvert.",
    ])
    return P.ecrire("planche-1-cuve.svg")


# ====================================================================== PLANCHE 2 : CHASSIS DE CUVE
def planche_chassis():
    P = Planche(2, "Châssis de cuve et portique (×2)", "1:10")
    F = Vue(P, 95, 235, 10)
    F.titre(0, -90, "VUE DE FACE")
    for s in (-1, 1):
        F.rect(s * 260, 0, s * 300, 840, 0.45)
        F.rect(s * 260, 840, s * 300, 1440, 0.45)
    for z in (300, 820):
        F.rect(-300, z - 20, 300, z + 20, 0.4)
    F.rect(-320, 840, 320, 846, 0.4, "#bbb")
    F.rect(-300, 1400, 300, 1440, 0.45)
    F.rect(-70, 1440, 70, 1448, 0.4, "#bbb")
    F.rect(-210, 846, 210, 896, 0.25, dash="2,1")
    F.rect(-200, 900, 200, 1300, 0.25, dash="2,1")
    F.texte(0, 1100, "cuve (pointillé)", 2.4)
    F.cote_v(0, 840, -380, "840", (-300, -300))
    F.cote_v(0, 1440, -430, "1440", (-300, -300))
    F.cote_v(0, 300, 360, "300", (300, 300))
    F.cote_v(0, 820, 400, "820", (300, 300))
    F.cote_h(-300, 300, -40, "600", (0, 0))
    F.cote_h(-320, 320, 1520, "tablette 640", (846, 846))
    F.cote_v(840, 900, 260, "60", (210, 210))
    F.texte(0, 870, "fond de cuve à 900 du sol", 2.4)

    S = Vue(P, 250, 235, 10)
    S.titre(0, -90, "VUE DE CÔTÉ")
    for s in (-1, 1):
        S.rect(s * 260, 0, s * 300, 840, 0.45)
    S.rect(260, 840, 300, 1440, 0.45)
    for z in (300, 820):
        S.rect(-300, z - 20, 300, z + 20, 0.4)
    S.rect(-320, 840, 320, 846, 0.4, "#bbb")
    S.rect(-100, 1440, 300, 1448, 0.4, "#bbb")
    S.rect(-50, 1448, 50, 1730, 0.3, dash="2,1")
    S.texte(0, 1600, "motoréducteur", 2.4)
    S.cote_h(-100, 300, 1520, "platine 400", (1448, 1448))
    S.cote_h(-300, 300, -40, "600", (0, 0))
    S.texte(280, 1480, "portique à l'arrière", 2.4, "end")

    notes(P, 300, 50, [
        "NOTES",
        "• Cornière acier 40×40×4, soudée, peinture époxy.",
        "• Tablette tôle 640×640×6 sur la ceinture haute.",
        "• Portique : 2 montants 40×40 + poutre 600,",
        "  platine moteur 140×400×8 percée Ø 20 au centre",
        "  (axe de la cuve).",
        "• Ceintures à 300 et 820 (axe des cornières).",
        "• Prévoir le passage des goulottes vers le filtre.",
    ])
    return P.ecrire("planche-2-chassis-cuve.svg")


# ====================================================================== PLANCHE 3 : BROYEUR
def planche_broyeur():
    P = Planche(3, "Broyeur à boulets et chariot à trémie", "1:10 et 1:5")
    F = Vue(P, 85, 215, 10)
    F.titre(0, -110, "BROYEUR — VUE DE FACE (1:10)")
    for s in (-1, 1):
        F.rect(s * 310, 0, s * 350, 460, 0.45)
    for z in (150, 440):
        F.rect(-350, z - 20, 350, z + 20, 0.4)
    F.rect(-350, 170, 350, 176, 0.35, "#bbb")
    F.rect(-370, 490, 400, 510, 0.35)            # arbre de rouleau
    F.rect(-200, 480, 160, 520, 0.4, "#555")     # manchon caoutchouc
    F.rect(-200, 625 - 136.5, 190, 625 + 136.5, 0.5)
    F.rect(190, 625 - 136.5, 202, 625 + 136.5, 0.5, "#bbb")
    F.axe(-260, 625, 260, 625)
    F.rect(-195, 625 + 112, 175, 625 + 124, 0.25, dash="2,1")
    F.texte(0, 625 + 90, "releveurs (pointillé)", 2.3)
    F.rect(0, 175, 290, 325, 0.25, dash="2,1")
    F.texte(145, 245, "motoréducteur", 2.3)
    F.rect(365, 185, 415, 565, 0.35, dash="2,1")
    F.texte(390, 600, "carter", 2.3)
    F.cote_h(-350, 350, -40, "700", (0, 0))
    F.cote_v(0, 460, -420, "460", (-350, -350))
    F.cote_v(0, 500, -470, "500 (axe rouleaux)", (-370, -370))
    F.cote_v(0, 625, -520, "625 (axe tambour)", (-200, -200))
    F.cote_h(-200, 202, 820, "402 (tube 390 + couvercle 12)", (762, 762))
    F.cote_h(-200, 160, 380, "manchons 360", (480, 480))
    F.repere(-100, 760, -200, 900, "tube acier Ø 273 × 6 (DN 250)", "start")

    C = Vue(P, 330, 85, 5)
    C.titre(0, -175, "COUPE DU TAMBOUR (1:5)")
    C.circle(0, 0, 136.5, 0.5)
    C.circle(0, 0, 130.5, 0.4)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        cx, cy = 120.5 * math.cos(a), 120.5 * math.sin(a)
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        pts = [(cx + ux * 10 + vx * 6, cy + uy * 10 + vy * 6), (cx + ux * 10 - vx * 6, cy + uy * 10 - vy * 6),
               (cx - ux * 10 - vx * 6, cy - uy * 10 - vy * 6), (cx - ux * 10 + vx * 6, cy - uy * 10 + vy * 6)]
        C.poly(pts, 0.4, "#555")
    for s in (-1, 1):
        C.rect(s * 136.5, -17, s * 140, 17, 0.4, "#bbb")
        C.circle(s * 160, -100, 20, 0.35)
    C.texte(0, -110, "rouleaux Ø 40 à ±100, axe 125 plus bas", 2.3)
    C.cote_h(-136.5, 136.5, 160, "Ø 273", (0, 0))
    C.texte(0, 20, "3 releveurs 20×12 à 120°", 2.4)
    C.texte(0, -30, "bossages M16 de chaque côté", 2.4)
    C.texte(0, -45, "(tourillons de levage)", 2.4)

    G = Vue(P, 270, 236, 10)
    G.titre(250, -60, "CHARIOT À TRÉMIE — EN SERVICE (1:10)")
    a = math.radians(44)
    tip = (0, 560)
    top = (450 * math.cos(a), 560 + 450 * math.sin(a))
    nx, nz = -math.sin(a), math.cos(a)
    G.poly([tip, top, (top[0] + nx * 50, top[1] + nz * 50), (tip[0] + nx * 50, tip[1] + nz * 50)], 0.45)
    G.poly([(top[0] - 47, 861), (top[0] + 77, 861), (top[0] + 165, 1011), (top[0] - 135, 1011)], 0.45)
    G.rect(260, 50, 280, 820, 0.4)
    G.rect(120, 35, 420, 55, 0.4)
    for x in (150, 390):
        G.circle(x, 18, 18, 0.35)
    G.line(0, 560, 120, 560, w=0.2, dash="2,1")
    G.texte(70, 590, "44°", 2.6)
    G.cote_h(top[0] - 135, top[0] + 165, 1080, "trémie 300 × 300", (1011, 1011))
    G.cote_h(top[0] - 47, top[0] + 77, 820, "124", (861, 861))
    G.cote_v(861, 1011, top[0] + 230, "150", (top[0] + 165, top[0] + 165))
    G.cote_v(0, 820, 470, "820", (280, 280))
    G.cote_h(120, 420, -40, "base 300 × 260", (35, 35))
    G.texte(225, 690, "goulotte en U 450 × 120, joues 50", 2.4, "start")
    G.texte(-10, 520, "bout de goulotte dans le fût (≈ 70 mm)", 2.4, "start")

    notes(P, 20, 45, [
        "NOTES",
        "• Rien ne doit dépasser du tube de plus de 8 mm : les arbres",
        "  des rouleaux passent à 10 mm de la paroi.",
        "• Couvercle affleurant Ø 273 × 12 avec joint, charnière plate",
        "  côté arrière, 3 grenouillères plates (saillie 7 mm).",
        "• Manchons caoutchouc arrêtés 30 mm avant le couvercle.",
        "• Vitesse 55–60 tr/min ; motoréducteur 180–250 W, courroie sous carter.",
        "• Fût chargé ≈ 18 kg : levage au palan (potence, flèche 1,3 m à 1,85 m).",
    ], 2.6)
    return P.ecrire("planche-3-broyeur.svg")


# ====================================================================== PLANCHE 4 : FILTRE
def planche_filtre():
    P = Planche(4, "Filtre sous vide et transfert", "1:5")
    V = Vue(P, 140, 245, 5)
    V.titre(0, -60, "COUPE VERTICALE")
    prof_fut = [(0, 40), (170, 40), (190, 70), (190, 400), (170, 440), (50, 450), (50, 470)]
    for s in (-1, 1):
        V.poly([(s * x, z) for x, z in prof_fut], 0.5, close=False)
        V.rect(s * 185, 0, s * 195, 75, 0.35)
        V.rect(s * 185, 400, s * 195, 475, 0.35)
        V.poly([(s * 47, 476), (s * 53, 471), (s * 178, 530), (s * 178, 800)], 0.5, close=False)
    V.rect(-174, 545, 174, 549, 0.35, "#555")
    V.rect(-174, 549, 174, 553, 0.3, "#ddd")
    V.texte(0, 575, "toile PP sur tôle perforée", 2.4)
    V.rect(-62, 455, 62, 474, 0.35, "url(#hachures)")
    V.rect(190, 90, 250, 110, 0.35)
    V.circle(225, 100, 20, 0.4)
    V.rect(250, 94, 270, 106, 0.35)
    V.rect(-260, 350, -190, 370, 0.35)
    V.axe(0, -20, 0, 860)
    V.cote_h(-190, 190, -40, "Ø 380 (fût à bière inox 30–50 L)", (0, 0))
    V.cote_h(-178, 178, 860, "Ø 356", (800, 800))
    V.cote_v(0, 800, -300, "800", (-178, -178))
    V.cote_v(0, 470, -250, "470", (-50, -50))
    V.cote_v(0, 549, 300, "549 (toile)", (174, 174))
    V.cote_v(0, 100, 330, "100", (270, 270))
    V.cote_v(0, 360, -330, "360", (-260, -260))
    V.repere(225, 100, 300, 200, "vanne de vidange 1/2\" → pompe de transfert → R2")
    V.repere(-225, 360, -300, 450, "piquage de vide → piège → pompe", "end")
    V.repere(0, 465, 120, 420, "joint EPDM")

    notes(P, 260, 40, [
        "NOTES",
        "• Vide maximum :",
        "   −0,2 bar pour la liqueur et les boues (≥ 85 °C) ;",
        "   −0,5 bar pour l'hydrate (≈ 50 °C).",
        "  Au-delà, la liqueur chaude bout dans le récepteur.",
        "• Pompe à vide à membrane avec bouton de réglage + vacuomètre.",
        "• Pompe de transfert inox, 10–20 L/min, compatible soude.",
        "• Deux toiles : 5–10 µm (boues rouges), 10–25 µm (hydrate).",
        "• Les goulottes de R1 et R2 arrivent à 830 du sol,",
        "  au-dessus du bord de la cuve filtrante (800).",
        "• La galette sort par le haut avec sa toile.",
    ], 2.7)
    return P.ecrire("planche-4-filtre.svg")


if __name__ == "__main__":
    for f in (planche_cuve, planche_chassis, planche_broyeur, planche_filtre):
        print("écrit :", f())
