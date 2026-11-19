# Animation du procede bauxite -> alumine, sur le modele realiste (~105 s a 24 images/s).
# Chaque produit entre et sort par une vraie ouverture : couvercle du fut + chariot a tremie,
# trappes a charniere de R1 et R2, vannes et tuyaux, porte du four.
# A lancer depuis Blender (onglet Scripting) ; construire_usine.py et materiaux_realistes.py
# doivent etre dans le meme dossier.

import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

BASE = os.path.dirname(globals().get("__file__") or bpy.data.filepath)


def _executer(nom, espace):
    chemin = os.path.join(BASE, nom)
    exec(compile(open(chemin, encoding="utf-8").read(), chemin, "exec"), espace)


ns = {"__name__": "build"}
_executer("construire_usine.py", ns)
_executer("materiaux_realistes.py", {"__name__": "materiaux"})
lathe, rod, ball, box, mat, coll, hose = (ns[k] for k in ("lathe", "rod", "ball", "box", "mat", "coll", "hose"))
X_A0, X_R1, X_F, X_R2, X_K = (ns[k] for k in ("X_A0", "X_R1", "X_F", "X_R2", "X_K"))
D = bpy.data.objects
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 2520
sc.render.fps = 24
sim = coll("SIM_Animation")
rad = math.radians
rnd = random.Random(3)

# ------------------------------------------------------------------ outils
_reg = {}        # id -> {(chemin, image): interpolation}, applique a la fin


def reg(idb, path, f, kind):
    _reg.setdefault(idb, {})[(path, int(f))] = kind


def all_fcurves(idb):
    ad = getattr(idb, "animation_data", None)
    if not ad or not ad.action:
        return []
    act, out = ad.action, []
    if hasattr(act, "layers"):
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out.extend(cb.fcurves)
    elif hasattr(act, "fcurves"):
        out.extend(act.fcurves)
    return out


def apply_interpolations():
    for idb, keys in _reg.items():
        for fc in all_fcurves(idb):
            for kp in fc.keyframe_points:
                fr = int(round(kp.co.x))
                kind = keys.get((fc.data_path, fr)) or keys.get((None, fr))
                if kind == 'DOUX':              # depart et arrivee en douceur, trajet droit
                    kp.interpolation = 'SINE'
                    kp.easing = 'EASE_IN_OUT'
                elif kind:
                    kp.interpolation = kind
            fc.update()


def kloc(ob, f, loc, kind='DOUX'):
    ob.location = loc
    ob.keyframe_insert("location", frame=f)
    reg(ob, "location", f, kind)


def kscale(ob, f, s, kind='LINEAR'):
    ob.scale = (s, s, s) if isinstance(s, (int, float)) else s
    ob.keyframe_insert("scale", frame=f)
    reg(ob, "scale", f, kind)


def krot(ob, f, e, kind='DOUX'):
    ob.rotation_euler = e
    ob.keyframe_insert("rotation_euler", frame=f)
    reg(ob, "rotation_euler", f, kind)


def porter(ob, etapes):
    """Deplacement en lignes droites avec depart/arrivee doux : [(image, position, rotation ou None)]."""
    for f, p, r in etapes:
        kloc(ob, f, p)
        if r is not None:
            krot(ob, f, r)


def level(ob, pairs):
    """Niveau d'un liquide ou d'un gateau : echelle Z, objet cache quand il est vide."""
    n = len(pairs)
    for i, (f, s) in enumerate(pairs):
        nxt = pairs[i + 1][1] if i + 1 < n else s
        prv = pairs[i - 1][1] if i > 0 else 0
        if s > 0:
            kscale(ob, f, (1, 1, s), 'LINEAR')
        elif nxt > 0:
            if f > 1:
                kscale(ob, f - 1, 0, 'CONSTANT')
            kscale(ob, f, (1, 1, 0.002), 'LINEAR')
        elif prv > 0:
            kscale(ob, f, (1, 1, 0.002), 'CONSTANT')
            kscale(ob, f + 1, 0, 'CONSTANT')
        else:
            kscale(ob, f, 0, 'CONSTANT')


def visible(ob, f_on, f_off=None):
    """Objet invisible (echelle 0) sauf entre f_on et f_off."""
    if f_on > 1:
        kscale(ob, 1, 0, 'CONSTANT')
    kscale(ob, f_on, 1, 'CONSTANT')
    if f_off:
        kscale(ob, f_off, 0, 'CONSTANT')


def kmat(m, f, rgb, alpha, kind='LINEAR'):
    reg(m.node_tree, None, f, kind)
    reg(m, "diffuse_color", f, kind)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Base Color"].keyframe_insert("default_value", frame=f)
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Alpha"].keyframe_insert("default_value", frame=f)
    m.diffuse_color = (*rgb, alpha)
    m.keyframe_insert("diffuse_color", frame=f)


def kemission(m, f, v):
    entree = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]
    entree.default_value = v
    entree.keyframe_insert("default_value", frame=f)
    reg(m.node_tree, None, f, 'CONSTANT')


def empty(name, loc, rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    ob.rotation_euler = rot
    ob.empty_display_size = 0.04
    sim.objects.link(ob)
    return ob


def adopt(par, children):
    bpy.context.view_layer.update()
    inv = par.matrix_world.inverted()
    for ch in children:
        ch.parent = par
        ch.matrix_parent_inverse = inv


def named(prefix):
    return [o for o in D if o.name.startswith(prefix)]


def spin(ob, f0, f1, axis, deg_per_frame):
    e0 = [0, 0, 0]
    e1 = [0, 0, 0]
    e1[axis] = rad(deg_per_frame * (f1 - f0))
    krot(ob, f0, e0, 'LINEAR')
    krot(ob, f1, e1, 'LINEAR')


def flux(nom, chemin, n, f0, f1, fabrique, periode=16, jitter=0.012):
    """n petits objets qui parcourent 'chemin' en boucle entre f0 et f1 (versement, ecoulement)."""
    rr = random.Random(len(nom) * 97 + f0)
    pts = [Vector(p) for p in chemin]
    for i in range(n):
        ob = fabrique(nom, pts[0])
        visible(ob, f0, f1)
        f = f0 + int(i * periode / n)
        while f < f1:
            j = Vector((rr.uniform(-jitter, jitter), rr.uniform(-jitter, jitter), 0))
            for k, p in enumerate(pts):
                fk = f + periode - 1 if k == len(pts) - 1 else f + round(k * periode / (len(pts) - 1))
                kloc(ob, fk, p + j, 'LINEAR' if k < len(pts) - 1 else 'CONSTANT')
            f += periode


def bascule(r, h, angle=-110):
    """Decalage du point de versement (bord le plus bas) d'un recipient r x h incline autour de X."""
    a = rad(angle)
    return Vector((0, r * math.cos(a) - h * math.sin(a), r * math.sin(a) + h * math.cos(a)))


rnd2 = random.Random(11)


def caillou(name, loc, r=None):
    r = r or rnd2.uniform(0.016, 0.026)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts:
        v.co *= rnd2.uniform(0.75, 1.2)
    bmesh.ops.scale(bm, vec=(1.0, rnd2.uniform(0.7, 1.0), rnd2.uniform(0.6, 0.9)), verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(ns["M_BAUX"])
    ob = bpy.data.objects.new(name, me)
    sim.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (rnd2.uniform(0, 6.3), rnd2.uniform(0, 6.3), rnd2.uniform(0, 6.3))
    return ob


def bille(name, loc):
    return ball(name, 0.016, loc, ns["M_INOX"], sim)


def flocon(name, loc):
    return box(name, (0.012, 0.009, 0.004), loc, ns["M_BLANC"], sim,
               rot=(rnd2.uniform(0, 3), rnd2.uniform(0, 3), rnd2.uniform(0, 3)))


EAU    = ((0.60, 0.80, 0.95), 0.35)
PULPE  = ((0.40, 0.10, 0.05), 0.96)
AMBRE  = ((0.85, 0.55, 0.15), 0.50)
LAIT   = ((0.96, 0.96, 0.95), 0.96)
PALE   = ((0.75, 0.86, 0.92), 0.40)
Z0 = 0.90                                  # fond des cuves R1 et R2
ZD = 0.625                                 # axe du fut du broyeur
M_EAU = mat("SIM_jet_eau", EAU[0], 0, 0.1, alpha=0.55)
M_J_AMBRE = mat("SIM_jet_ambre", AMBRE[0], 0, 0.2, alpha=0.8)
M_TUYAU = mat("SIM_tuyau_arrosage", (0.03, 0.20, 0.04), 0, 0.45)

# ================================================================== 1. ENTREE dans le broyeur (40-380)
# fut + couvercle a charniere verticale (le couvercle s'ouvre comme une porte)
e_fut = empty("SIM_fut", (X_A0, 0, ZD))
e_lid = empty("SIM_charniere_couvercle_fut", (X_A0 + 0.208, 0.152, ZD))   # charniere a l'arriere
adopt(e_lid, named("A0_couvercle") + named("A0_cercle") + named("A0_levier"))
grille = []                                # grille de vidange (retient les billes)
for k in range(-3, 4):
    corde = 2 * math.sqrt(max(0.136 ** 2 - (k * 0.034) ** 2, 0.0))
    grille.append(box("SIM_grille_vidange", (0.004, 0.006, corde), (X_A0 + 0.185, k * 0.034, ZD), ns["M_TOLE"], sim))
    grille.append(box("SIM_grille_vidange", (0.004, corde, 0.006), (X_A0 + 0.185, 0, ZD + k * 0.034), ns["M_TOLE"], sim))
adopt(e_fut, named("A0_fut") + named("A0_bourrelet") + named("A0_charniere") + [e_lid] + grille)

for f, a in ((1, 0), (50, 0), (66, 115), (362, 115), (378, 0),
             (565, 0), (580, 115), (762, 115), (778, 0)):
    krot(e_lid, f, (0, 0, rad(a)))

# chariot a tremie : il roule de sa place de garage jusqu'a l'ouverture du fut, puis repart
e_cart = empty("SIM_chariot", (X_A0 + 0.80, 0, 0))
adopt(e_cart, named("A0_goulotte") + named("A0_tremie") + named("A0_chariot"))
for f, x in ((1, 0.80), (66, 0.80), (90, 0.40), (340, 0.40), (362, 0.80)):
    kloc(e_cart, f, (X_A0 + x, 0, 0))

# trajet des morceaux : tremie -> goulotte -> fond du fut
P_TREMIE = Vector((X_A0 + 0.469, -0.04, 1.12))
GLISSE = [P_TREMIE, (X_A0 + 0.469, -0.01, 0.99), (X_A0 + 0.44, 0, 0.887), (X_A0 + 0.116, 0, 0.574),
          (X_A0 - 0.02, 0, 0.515)]

# seau de bauxite brute (morceaux)
BX, BY = X_A0 - 0.14, -0.50
seau_b = lathe("SIM_seau_bauxite_brute", [(0, 0), (0.09, 0), (0.105, 0.17), (0.10, 0.17), (0.086, 0.004), (0, 0.004)],
               ns["M_NOIR"], sim, (BX, BY, 0))
tas = []
for i in range(18):
    a_ = rnd2.uniform(0, math.tau)
    rr_ = rnd2.uniform(0, 0.055)
    tas.append(caillou("SIM_bauxite_brute", (BX + rr_ * math.cos(a_), BY + rr_ * math.sin(a_),
                                             0.035 + (i // 6) * 0.05 + rnd2.uniform(0, 0.02)), rnd2.uniform(0.022, 0.034)))
adopt(seau_b, tas)
o_seau = P_TREMIE - bascule(0.105, 0.17)
porter(seau_b, [(1, (BX, BY, 0), (0, 0, 0)), (92, (BX, BY, 0), None), (108, (BX, BY, 1.32), None),
                (128, (o_seau.x, o_seau.y, 1.32), (0, 0, 0)), (134, o_seau, None), (146, o_seau, (rad(-110), 0, 0)),
                (196, o_seau, (rad(-110), 0, 0)), (208, o_seau, (0, 0, 0)), (214, (o_seau.x, o_seau.y, 1.32), None),
                (232, (BX, BY, 1.32), None), (246, (BX, BY, 0), None)])
for i, ob in enumerate(tas):                      # le tas se vide pendant le versement
    visible(ob, 1, 148 + i * 3)
flux("SIM_flux_bauxite", GLISSE, 9, 146, 198, caillou, periode=24)

# bac de billes d'acier
TX, TY = X_A0 + 0.30, -0.45
bac_b = lathe("SIM_bac_billes", [(0, 0), (0.075, 0), (0.085, 0.06), (0.082, 0.06), (0.072, 0.003), (0, 0.003)],
              ns["M_TOLE"], sim, (TX, TY, 0))
tas_b = []
for i in range(10):
    a_ = rnd2.uniform(0, math.tau)
    rr_ = rnd2.uniform(0, 0.045)
    tas_b.append(bille("SIM_bille_tas", (TX + rr_ * math.cos(a_), TY + rr_ * math.sin(a_), 0.02 + (i // 5) * 0.025)))
adopt(bac_b, tas_b)
o_bac = P_TREMIE - bascule(0.085, 0.06)
porter(bac_b, [(1, (TX, TY, 0), (0, 0, 0)), (246, (TX, TY, 0), None), (258, (TX, TY, 1.24), None),
               (274, (o_bac.x, o_bac.y, 1.24), (0, 0, 0)), (278, o_bac, None), (288, o_bac, (rad(-110), 0, 0)),
               (318, o_bac, (rad(-110), 0, 0)), (326, o_bac, (0, 0, 0)), (330, (o_bac.x, o_bac.y, 1.24), None),
               (344, (TX, TY, 1.24), None), (356, (TX, TY, 0), None)])
for i, ob in enumerate(tas_b):
    visible(ob, 1, 290 + i * 3)
flux("SIM_flux_billes", GLISSE, 6, 288, 320, bille, periode=22)

# ================================================================== 2. BROYAGE (380-560) : 4 tours exacts
spin(e_fut, 380, 560, 0, -8)
ROT_FIN = rad(-8 * 180)

# ================================================================== 3. VIDANGE (565-780) : grille, fut incline au-dessus du bac
for ob in grille:
    visible(ob, 580, 760)
BAC = Vector((X_A0 + 0.65, -0.45, 0))
haut = 0.95
for f, p, ry in ((585, (X_A0, 0, ZD), 0), (600, (X_A0, 0, haut), 0), (620, (BAC.x, BAC.y, haut), 0),
                 (636, (BAC.x, BAC.y, haut), 90), (648, (BAC.x, BAC.y, 0.55), 90), (700, (BAC.x, BAC.y, 0.55), 90),
                 (712, (BAC.x, BAC.y, haut), 90), (728, (BAC.x, BAC.y, haut), 0), (748, (X_A0, 0, haut), 0),
                 (760, (X_A0, 0, ZD), 0)):
    kloc(e_fut, f, p)
    krot(e_fut, f, (ROT_FIN, rad(ry), 0))
jet_a0 = rod("SIM_flux_poudre_vidange", (BAC.x, BAC.y, 0.35), (BAC.x, BAC.y, 0.06), 0.022, ns["M_BAUX"], sim)
visible(jet_a0, 650, 700)

e_bin = empty("SIM_bac_poudre", BAC)
poudre_bin = lathe("SIM_poudre_dans_bac", [(0, 0), (0.10, 0), (0.111, 0.11), (0, 0.11)], ns["M_BAUX"], sim,
                   (BAC.x, BAC.y, 0.004))
adopt(e_bin, [D["A0_bac_poudre"], poudre_bin])
level(poudre_bin, ((1, 0), (652, 0), (700, 1.0), (1068, 1.0), (1110, 0)))

# ================================================================== 4. CHARGEMENT de R1 (780-1170) par la trappe
def charniere(tag, angle_monde):
    """Empty a la charniere de la trappe ; son axe X est tangent au couvercle."""
    side = 1 if tag.startswith("R1") else -1
    X = X_R1 if side > 0 else X_R2
    th = rad(345)
    h = (X + side * 0.177 * math.cos(th), 0.177 * math.sin(th), 1.333)
    g = rad(angle_monde + 90)
    e = empty("SIM_charniere_" + tag, h, (0, 0, g))
    adopt(e, [D[tag + "_trappe_couvercle"], D[tag + "_trappe_bouton"]])
    return e, g


def ouvrir_trappe(e, g, f_ouvre, f_ferme):
    for f, a in ((1, 0), (f_ouvre, 0), (f_ouvre + 15, 110), (f_ferme, 110), (f_ferme + 15, 0)):
        krot(e, f, (rad(a), 0, g))


e_t1, g1 = charniere("R1_Attaque", -15)
e_t2, g2 = charniere("R2_Precipitation", 195)
ouvrir_trappe(e_t1, g1, 780, 1155)
ouvrir_trappe(e_t2, g2, 1660, 1772)
H1 = Vector((X_R1 + 0.125 * math.cos(rad(345)), 0.125 * math.sin(rad(345)), 0))
H2 = Vector((X_R2 - 0.125 * math.cos(rad(345)), 0.125 * math.sin(rad(345)), 0))

# 4a. l'eau arrive par un tuyau depuis le robinet
rxr, ryr = X_R1 - 0.70, 0.35
tuyau_eau = hose("SIM_tuyau_eau", [(rxr, ryr - 0.06, 0.83), (rxr + 0.10, -0.30, 0.65), (X_R1 - 0.25, -0.42, 1.60),
                                   (H1.x, H1.y, 1.52), (H1.x, H1.y, 1.36)], 0.011, M_TUYAU, sim)
visible(tuyau_eau, 795, 880)
jet_eau = rod("SIM_jet_eau_R1", (H1.x, H1.y, 1.36), (H1.x, H1.y, Z0 + 0.01), 0.008, M_EAU, sim)
visible(jet_eau, 805, 870)
e_rob = empty("SIM_manette_robinet", (rxr, ryr - 0.03, 0.885))
adopt(e_rob, [D["Robinet_manette"]])
for f, a in ((1, 0), (798, 0), (804, 90), (870, 90), (876, 0)):
    krot(e_rob, f, (0, 0, rad(a)))

# 4b. la soude, versee dans l'eau par la trappe
P_R1 = Vector((H1.x, H1.y, 1.47))
SX, SY = X_R1 - 0.45, -0.62
pot = lathe("SIM_pot_soude", [(0, 0), (0.08, 0), (0.085, 0.15), (0.082, 0.15), (0.077, 0.004), (0, 0.004)],
            ns["M_BLANC"], sim, (SX, SY, 0))
tas_s = lathe("SIM_soude_paillettes", [(0, 0), (0.077, 0), (0.080, 0.11), (0, 0.11)], ns["M_BLANC"], sim, (SX, SY, 0.004))
adopt(pot, [tas_s])
o_pot = P_R1 - bascule(0.085, 0.15)
porter(pot, [(1, (SX, SY, 0), (0, 0, 0)), (880, (SX, SY, 0), None), (892, (SX, SY, 1.66), None),
             (910, (o_pot.x, o_pot.y, 1.66), (0, 0, 0)), (914, o_pot, None), (924, o_pot, (rad(-110), 0, 0)),
             (960, o_pot, (rad(-110), 0, 0)), (968, o_pot, (0, 0, 0)), (972, (o_pot.x, o_pot.y, 1.66), None),
             (988, (SX, SY, 1.66), None), (1000, (SX, SY, 0), None)])
kscale(tas_s, 924, (1, 1, 1))
kscale(tas_s, 960, (1, 1, 0.03))
flux("SIM_flux_soude", [P_R1, (H1.x, H1.y, 1.30), (H1.x, H1.y, 1.03)], 8, 924, 962, flocon, periode=14, jitter=0.008)

# 4c. la poudre de bauxite : le bac est porte du broyeur jusqu'a la trappe
o_bin = P_R1 - bascule(0.12, 0.22)
DEPOT = (X_R1 - 0.20, -0.62, 0)
porter(e_bin, [(1, BAC, (0, 0, 0)), (1000, BAC, None), (1015, (BAC.x, BAC.y, 1.72), None),
               (1045, (o_bin.x, o_bin.y, 1.72), (0, 0, 0)), (1050, o_bin, None), (1062, o_bin, (rad(-110), 0, 0)),
               (1110, o_bin, (rad(-110), 0, 0)), (1118, o_bin, (0, 0, 0)), (1124, (o_bin.x, o_bin.y, 1.72), None),
               (1140, (DEPOT[0], DEPOT[1], 1.72), None), (1155, DEPOT, None)])
jet_p = rod("SIM_flux_poudre_R1", P_R1, (H1.x, H1.y, 1.06), 0.016, ns["M_BAUX"], sim)
visible(jet_p, 1064, 1110)

liq1 = D["R1_Attaque_liquide"]
liq1.location.z += 0.0005
m1 = liq1.data.materials[0]
level(liq1, ((1, 0), (805, 0), (870, 0.50), (924, 0.50), (960, 0.57), (1064, 0.57), (1110, 0.65),
             (1420, 0.65), (1500, 0.25), (1520, 0.25), (1580, 0)))
for f, (rgb, a) in ((805, EAU), (1064, EAU), (1110, PULPE), (1330, PULPE), (1410, AMBRE)):
    kmat(m1, f, rgb, a)


def agitateur(tag, X, f0, f1):
    e = empty("SIM_rot_" + tag, (X, 0, 1.0))
    adopt(e, named(tag + "_arbre") + named(tag + "_moyeu") + named(tag + "_pale") + named(tag + "_accouplement"))
    spin(e, f0, f1, 2, 9)


agitateur("R1_Attaque", X_R1, 900, 1330)
agitateur("R2_Precipitation", X_R2, 1790, 2010)

# ================================================================== 5-6. ATTAQUE puis DECANTATION dans R1
boue1 = lathe("SIM_boue_decantee", [(0, 0), (0.1965, 0), (0.1965, 0.045), (0, 0.045)],
              ns["M_BOUE"], sim, (X_R1, 0, Z0 + 0.007), -45.6, 271.2)
level(boue1, ((1, 0), (1330, 0), (1410, 1), (1520, 1), (1580, 0)))

# ================================================================== 7. FILTRATION de R1 par les vannes
def vanne(tag, nom, x, y, z, f_open, f_close):
    e = empty(f"SIM_rot_vanne_{tag}_{nom}", (x, y, z))
    adopt(e, [D[f"{tag}_poignee_{nom}"]])
    for f, a in ((1, 0), (f_open, 0), (f_open + 10, 90), (f_close, 90), (f_close + 10, 0)):
        krot(e, f, (0, 0, rad(a)), 'LINEAR')


sx, sy = 0.335 * math.cos(rad(15)), 0.335 * math.sin(rad(15))
vanne("R1_Attaque", "haute", X_R1 + sx, sy, Z0 + 0.075, 1410, 1500)
vanne("R1_Attaque", "basse", X_R1 + sx, -sy, Z0 + 0.022, 1510, 1580)
vanne("R2_Precipitation", "basse", X_R2 - sx, -sy, Z0 + 0.022, 2010, 2100)

jet1 = rod("SIM_jet_liqueur", (-0.11, 0.03, 0.83), (-0.11, 0.03, 0.56), 0.012, M_J_AMBRE, sim)
visible(jet1, 1420, 1500)
jet2 = rod("SIM_jet_boue", (-0.11, -0.03, 0.83), (-0.11, -0.03, 0.56), 0.014, ns["M_BOUE"], sim)
visible(jet2, 1520, 1580)
jet3 = rod("SIM_jet_hydrate", (0.11, -0.03, 0.83), (0.11, -0.03, 0.56), 0.014, ns["M_BLANC"], sim)
visible(jet3, 2020, 2100)

M_FILTRAT = mat("SIM_mat_filtrat", AMBRE[0], 0, 0.3, alpha=AMBRE[1])
filtrat = lathe("SIM_filtrat_dans_fut", [(0, 0), (0.169, 0), (0.187, 0.028), (0.187, 0.26), (0, 0.26)],
                M_FILTRAT, sim, (X_F, 0, 0.0435), -45, 270)
level(filtrat, ((1, 0), (1420, 0), (1500, 0.65), (1520, 0.65), (1580, 0.80), (1685, 0.80), (1760, 0),
                (2020, 0), (2100, 0.9)))
kmat(M_FILTRAT, 1, *AMBRE, kind='CONSTANT')
kmat(M_FILTRAT, 1770, *PALE, kind='CONSTANT')

# manometre de la pompe a vide
axe = D["F_pompe_axe_aiguille"]
e_aig = empty("SIM_rot_aiguille", axe.location.copy())
adopt(e_aig, [D["F_pompe_aiguille"]])
for f, a in ((1, -75), (1410, -75), (1430, 0), (1580, 0), (1600, -75), (2010, -75), (2030, 0),
             (2100, 0), (2120, -75)):
    krot(e_aig, f, (0, rad(a), 0))

# ================================================================== 8. la galette de boue rouge sort PAR LE HAUT du filtre
for o in named("F_gateau_boue_rouge"):
    bpy.data.objects.remove(o)
gat_b = lathe("SIM_gateau_boue_rouge", [(0, 0), (0.162, 0), (0.162, 0.032), (0, 0.032)],
              ns["M_BOUE"], sim, (X_F, 0, 0.553))
level(gat_b, ((1, 0), (1520, 0), (1585, 1)))
lathe("SIM_bac_boues_rouges", [(0, 0), (0.19, 0), (0.21, 0.18), (0.205, 0.18), (0.186, 0.004), (0, 0.004)],
      ns["M_BAC"], sim, (-0.55, -0.85, 0))
porter(gat_b, [(1595, (X_F, 0, 0.553), None), (1612, (X_F, 0, 1.0), None), (1638, (-0.55, -0.85, 1.0), None),
               (1655, (-0.55, -0.85, 0.03), None)])

# ================================================================== 9. TRANSFERT de la liqueur vers R2 : vanne, pompe, trappe
e_vid = empty("SIM_rot_vanne_vidange", (X_F + 0.225, 0, 0.128))
adopt(e_vid, [D["F_poignee_vidange"]])
for f, a in ((1, 0), (1675, 0), (1682, 90), (1762, 90), (1769, 0)):
    krot(e_vid, f, (0, 0, rad(a)), 'LINEAR')
qx, qy = X_F + 0.36, -0.30
tuyau_t = hose("SIM_tuyau_transfert", [(qx - 0.05, qy, 0.16), (qx + 0.04, -0.42, 0.70), (X_R2 - 0.30, -0.36, 1.55),
                                       (H2.x, H2.y, 1.52), (H2.x, H2.y, 1.36)], 0.010, ns["M_NOIR"], sim)
visible(tuyau_t, 1676, 1770)
jet_t = rod("SIM_jet_liqueur_R2", (H2.x, H2.y, 1.36), (H2.x, H2.y, Z0 + 0.01), 0.009, M_J_AMBRE, sim)
visible(jet_t, 1685, 1760)
liq2 = D["R2_Precipitation_liquide"]
liq2.location.z += 0.0005
m2 = liq2.data.materials[0]
level(liq2, ((1, 0), (1685, 0), (1760, 1.0), (2020, 1.0), (2100, 0)))
for f, (rgb, a) in ((1685, AMBRE), (1810, AMBRE), (1990, LAIT)):
    kmat(m2, f, rgb, a)

# ================================================================== 10. PRECIPITATION au CO2 (par le tube plongeur)
M_BULLE = mat("SIM_bulle_CO2", (1, 1, 1), 0, 0.1, emit=0.6)
zb, zt = Z0 + 0.04, Z0 + 0.225
for i in range(34):
    if i < 14:
        th = 224.0 if i % 2 else 316.0
        r = rnd.uniform(0.03, 0.18)
    else:
        th = rnd.uniform(-40, 220)
        r = rnd.uniform(0.04, 0.17)
    x, y = X_R2 + r * math.cos(rad(th)), r * math.sin(rad(th))
    b = ball("SIM_bulle", rnd.uniform(0.005, 0.009), (x, y, zb), M_BULLE, sim)
    visible(b, 1792, 2010)
    f = 1790 + rnd.randint(0, 25)
    while f < 2010:
        p = rnd.randint(20, 32)
        kloc(b, f, (x, y, zb), 'LINEAR')
        kloc(b, f + p - 1, (x + rnd.uniform(-0.01, 0.01), y, zt), 'CONSTANT')
        f += p

# ================================================================== 11. FILTRATION de l'hydrate, puis depot dans le creuset
hyd = lathe("SIM_gateau_hydrate", [(0, 0), (0.162, 0), (0.162, 0.05), (0, 0.05)],
            ns["M_BLANC"], sim, (X_F, 0, 0.553))
level(hyd, ((1, 0), (2020, 0), (2100, 1)))

xcK, ycK = X_K - 0.08, -0.08               # centre de la chambre du four
TABLE = Vector((X_K + 0.60, -0.10, 0.628))  # creuset en attente sur la table de preparation
porter(hyd, [(2120, (X_F, 0, 0.553), None), (2135, (X_F, 0, 1.05), None), (2150, (0.30, -0.62, 1.05), None),
             (2180, (TABLE.x, -0.62, 1.05), None), (2192, (TABLE.x, TABLE.y, 1.05), None),
             (2204, (TABLE.x, TABLE.y, TABLE.z + 0.012), None)])
kscale(hyd, 2192, (1, 1, 1))
kscale(hyd, 2204, (0.42, 0.42, 0.42))
kscale(hyd, 2205, 0, 'CONSTANT')

# creuset : modelise dans la chambre ; un empty le porte (table -> four -> table)
e_gaz = empty("SIM_creuset", (xcK, ycK, 0.628))
alu = D["K_alumine"]
h = alu.dimensions.z / 2
alu.data.transform(Matrix.Translation((0, 0, h)))
alu.location.z -= h
adopt(e_gaz, named("K_gazette") + [alu])
kscale(alu, 1, 0, 'CONSTANT')
kscale(alu, 2204, 1, 'LINEAR')
kscale(alu, 2295, (1, 1, 1), 'LINEAR')
kscale(alu, 2370, (1, 1, 0.65), 'LINEAR')    # perte de masse : l'eau part

# ================================================================== 12. le creuset entre PAR LA PORTE, a plat
DEVANT = (xcK, -0.62, 0.64)
porter(e_gaz, [(1, TABLE, None), (2210, TABLE, None), (2216, (TABLE.x, TABLE.y, 0.64), None),
               (2236, DEVANT, None), (2256, (xcK, ycK, 0.64), None), (2262, (xcK, ycK, 0.628), None),
               (2420, (xcK, ycK, 0.628), None), (2426, (xcK, ycK, 0.64), None), (2444, DEVANT, None),
               (2462, (TABLE.x, TABLE.y, 0.64), None), (2468, TABLE, None)])

# ================================================================== 13-14. CALCINATION et REFROIDISSEMENT
e_porte = empty("SIM_rot_porte", (X_K - 0.28, -0.23, 0.80))
adopt(e_porte, named("K_porte") + named("K_poignee_porte"))
for f, a in ((1, 0), (2265, 0), (2290, 100), (2395, 100), (2415, 0)):
    krot(e_porte, f, (0, 0, rad(a)))

pv = D["K_afficheur_PV"]
seq = ((1, "25"), (2292, "150"), (2302, "290"), (2312, "400"), (2330, "560"), (2340, "780"),
       (2350, "960"), (2358, "1050"), (2374, "820"), (2380, "540"), (2386, "260"), (2392, "95"),
       (2420, "60"))
textes = [pv]
for _, txt in seq[1:]:
    ob = pv.copy()
    ob.data = pv.data.copy()
    ob.data.body = txt
    sim.objects.link(ob)
    textes.append(ob)
pv.data.body = seq[0][1]
for i, (ob, (f0, _)) in enumerate(zip(textes, seq)):
    visible(ob, f0, seq[i + 1][0] if i + 1 < len(seq) else None)

m_vc = mat("SIM_voyant_chauffe", (0.6, 0.02, 0.01), 0, 0.3, emit=4.0)
D["K_voyant_chauffe"].data.materials[0] = m_vc
for f, v in ((1, 0.0), (2292, 4.0), (2365, 0.0)):
    kemission(m_vc, f, v)

M_VAPEUR = mat("SIM_vapeur", (1, 1, 1), 0, 0.9, alpha=0.5)
for i in range(7):
    v = ball("SIM_vapeur", 0.02, (xcK, ycK, 1.04), M_VAPEUR, sim)
    kscale(v, 1, 0, 'CONSTANT')
    f = 2300 + i * 5
    while f < 2352:
        kloc(v, f, (xcK, ycK, 1.04), 'LINEAR')
        kscale(v, f, 0.6, 'LINEAR')
        kloc(v, f + 33, (xcK + rnd.uniform(-0.08, 0.08), ycK, 1.50), 'CONSTANT')
        kscale(v, f + 33, 2.2, 'CONSTANT')
        f += 35
    kscale(v, f, 0, 'CONSTANT')

# ================================================================== CAMERA
cam = sc.camera
cam.data.lens = 35
cible = empty("SIM_cible_camera", (0.05, 0, 0.85))
con = cam.constraints.new('TRACK_TO')
con.target = cible
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
plans = (
    ((1, 30),       (0.4, -7.7, 2.9),     (0.05, 0, 0.85)),       # vue d'ensemble
    ((58, 372),     (-1.25, -1.85, 1.45), (-2.05, -0.12, 0.72)),  # entree dans le broyeur
    ((392, 770),    (-1.20, -2.10, 1.25), (-1.95, -0.25, 0.55)),  # broyage + vidange
    ((790, 1160),   (-0.30, -2.30, 1.85), (-1.05, -0.15, 1.05)),  # chargement de R1
    ((1175, 1400),  (-0.55, -2.50, 1.75), (-0.85, 0.00, 1.10)),   # attaque, decantation
    ((1415, 1655),  (-0.35, -2.90, 1.60), (-0.40, 0.00, 0.75)),   # filtration, boue rouge
    ((1668, 2110),  (0.45, -2.90, 1.70),  (0.45, 0.00, 0.85)),    # transfert, precipitation, filtration
    ((2125, 2200),  (1.55, -3.90, 2.00),  (1.55, -0.25, 0.80)),   # hydrate -> creuset
    ((2212, 2445),  (2.90, -2.15, 1.35),  (2.68, -0.20, 0.72)),   # four
    ((2470, 2520),  (3.30, -1.55, 1.25),  (2.95, -0.10, 0.65)),   # alumine sur la table
)
for (fa, fb), pc, pt in plans:
    for f in (fa, fb):
        kloc(cam, f, pc)
        kloc(cible, f, pt)

# ================================================================== LEGENDES a l'ecran
M_HUD = mat("SIM_texte_ecran", (1, 1, 1), 0, 0.5, emit=1.5)
M_BANDE = mat("SIM_bandeau", (0, 0, 0), 0, 0.9, alpha=0.6)
bande = box("SIM_bandeau", (1.04, 0.062, 0.001), (0, 0, 0), M_BANDE, sim)
bande.parent = cam
bande.visible_shadow = False
bande.location = (0, -0.236, -1.004)
legendes = (
    (1,    "De la bauxite à l'alumine  -  lot de 5 kg"),
    (40,   "1. ENTRÉE  -  on ouvre le fût, le chariot à trémie s'avance"),
    (130,  "5 kg de bauxite brute versés dans la trémie, ils glissent dans le fût"),
    (250,  "Puis les billes d'acier ; le chariot recule, on referme le fût"),
    (380,  "2. BROYAGE  -  la bauxite est réduite en poudre (< 250 µm)"),
    (565,  "3. VIDANGE  -  une grille retient les billes, la poudre tombe dans le bac"),
    (780,  "4. CHARGEMENT de R1  -  l'eau arrive par la trappe"),
    (880,  "Puis 3,5 kg de soude, toujours versée dans l'eau"),
    (1000, "Puis les 5 kg de poudre de bauxite"),
    (1170, "5. ATTAQUE  -  100 °C, 2 h : l'alumine se dissout dans la soude"),
    (1330, "6. DÉCANTATION  -  les boues rouges tombent au fond"),
    (1410, "7. FILTRATION  -  vanne haute : la liqueur claire passe"),
    (1510, "Vanne basse : les boues rouges restent sur la toile"),
    (1590, "La galette de boue rouge est sortie par le haut du filtre"),
    (1660, "8. TRANSFERT  -  pompe : la liqueur entre dans R2 par la trappe"),
    (1790, "9. PRÉCIPITATION  -  le CO2 fait apparaître l'hydrate blanc"),
    (2010, "10. FILTRATION  -  l'hydrate d'alumine reste sur la toile"),
    (2115, "11. L'hydrate est déposé dans le creuset"),
    (2208, "12. Le creuset entre dans le four par la porte"),
    (2266, "13. CALCINATION  -  montée à 1050 °C : l'eau part en vapeur"),
    (2366, "14. REFROIDISSEMENT  -  porte fermée jusqu'à moins de 100 °C"),
    (2420, "ALUMINE  -  environ 1,9 kg de poudre blanche"),
)
for i, (f0, txt) in enumerate(legendes):
    cu = bpy.data.curves.new(f"SIM_legende_{i:02d}", 'FONT')
    cu.body = txt
    cu.size = 0.027
    cu.align_x = 'CENTER'
    cu.materials.append(M_HUD)
    ob = bpy.data.objects.new(f"SIM_legende_{i:02d}", cu)
    sim.objects.link(ob)
    ob.parent = cam
    ob.visible_shadow = False
    ob.location = (0, -0.245, -1.0)
    f1 = legendes[i + 1][0] if i + 1 < len(legendes) else None
    visible(ob, f0, f1)

apply_interpolations()

# liquides semi-transparents : melange lisse plutot que tramage (sinon effet granuleux)
for m in (m1, m2, M_FILTRAT, M_J_AMBRE, M_VAPEUR, M_EAU):
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass

# lecture fluide dans la fenetre : images sautees si l'ordinateur est trop lent
try:
    sc.sync_mode = 'FRAME_DROP'
except TypeError:
    pass
sc.frame_set(1)
print("Animation prete :", sc.frame_end, "images,", round(sc.frame_end / sc.render.fps), "s")
