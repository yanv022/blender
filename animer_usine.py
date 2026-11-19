# Animation du procede bauxite -> alumine, sur le modele realiste (~105 s a 24 images/s).
# Chaque produit entre et sort par une vraie ouverture : couvercle du fut + chariot a tremie,
# trappes a charniere de R1 et R2, vannes et tuyaux, porte du four. Le fut est leve au palan.
# Precipitation par amorcage (la liqueur epuisee repart a l'attaque du lot suivant).
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
etiquette = ns["etiquette"]
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
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for s, v in ((bsdf.inputs["Base Color"], (*rgb, 1)), (bsdf.inputs["Alpha"], alpha)):
        s.default_value = v
        s.keyframe_insert("default_value", frame=f)
        reg(m.node_tree, s.path_from_id("default_value"), f, kind)
    m.diffuse_color = (*rgb, alpha)
    m.keyframe_insert("diffuse_color", frame=f)
    reg(m, "diffuse_color", f, kind)


def kemission(m, f, v):
    s = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]
    s.default_value = v
    s.keyframe_insert("default_value", frame=f)
    reg(m.node_tree, s.path_from_id("default_value"), f, 'CONSTANT')


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


def anse(nom, base, r, h):
    """Anse metallique de seau, articulee sur l'axe de basculement (cotes +-X)."""
    x, y, z0 = base
    pts = [(x - r, y, z0 + h), (x - 0.7 * r, y, z0 + h + 0.6 * r), (x, y, z0 + h + 0.85 * r),
           (x + 0.7 * r, y, z0 + h + 0.6 * r), (x + r, y, z0 + h)]
    return hose(nom, pts, 0.0035, ns["M_INOX"], sim)


def afficheur(ob_pv, seq):
    """Afficheur de temperature : une copie du texte par valeur, affichee a tour de role."""
    textes = [ob_pv]
    for _, txt in seq[1:]:
        ob = ob_pv.copy()
        ob.data = ob_pv.data.copy()
        ob.data.body = txt
        for c in ob_pv.users_collection:
            c.objects.link(ob)
        textes.append(ob)
    ob_pv.data.body = seq[0][1]
    for i, (ob, (f0, _)) in enumerate(zip(textes, seq)):
        visible(ob, f0, seq[i + 1][0] if i + 1 < len(seq) else None)


def agiter_liquide(m, f0, f1):
    """Surface du liquide qui bouge pendant l'agitation (relief anime)."""
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    co = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    try:
        nz.noise_dimensions = '4D'
    except Exception:
        pass
    nz.inputs["Scale"].default_value = 30.0
    nt.links.new(co.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    w = nz.inputs["W"]
    st = bp.inputs["Strength"]
    for f, wv, sv in ((1, 0.0, 0.0), (f0, 0.0, 0.25), (f1, (f1 - f0) * 0.06, 0.0)):
        w.default_value = wv
        w.keyframe_insert("default_value", frame=f)
        reg(nt, w.path_from_id("default_value"), f, 'LINEAR')
        st.default_value = sv
        st.keyframe_insert("default_value", frame=f)
        reg(nt, st.path_from_id("default_value"), f, 'CONSTANT')


_n_jet = [0]


def jet(nom, haut, bas, r, m, f0, f1):
    """Ecoulement de liquide : colonne subdivisee, un peu effilee, ondulee par une texture qui descend."""
    haut, bas = Vector(haut), Vector(bas)
    L = (haut - bas).length
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r * 0.75, radius2=r, depth=L)
    vert = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > L * 0.9]
    bmesh.ops.subdivide_edges(bm, edges=vert, cuts=20, use_grid_fill=True)
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    ob = bpy.data.objects.new(nom, me)
    sim.objects.link(ob)
    ob.location = (haut + bas) / 2
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(haut - bas)
    _n_jet[0] += 1
    tex = bpy.data.textures.new(f"SIM_tex_jet_{_n_jet[0]}", 'CLOUDS')
    tex.noise_scale = 0.03
    e = empty(f"SIM_flot_{_n_jet[0]}", ob.location)
    md = ob.modifiers.new("Ondulation", 'DISPLACE')
    md.texture = tex
    md.texture_coords = 'OBJECT'
    md.texture_coords_object = e
    md.strength = r * 0.6
    md.mid_level = 0.5
    kloc(e, f0, e.location.copy(), 'LINEAR')
    kloc(e, f1, e.location + Vector((0, 0, 0.012 * (f1 - f0))), 'LINEAR')
    visible(ob, f0, f1)
    return ob


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


def grain(name, loc):                       # grain de poudre de bauxite
    return ball(name, rnd2.uniform(0.004, 0.007), loc, ns["M_BAUX"], sim)


def grain_blanc(name, loc):                 # grain d'hydrate (amorce)
    return ball(name, rnd2.uniform(0.004, 0.007), loc, ns["M_BLANC"], sim)


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
RD = 0.14
M_EAU = mat("SIM_jet_eau", EAU[0], 0, 0.1, alpha=0.55)
M_J_AMBRE = mat("SIM_jet_ambre", AMBRE[0], 0, 0.2, alpha=0.8)
M_J_BOUE = mat("SIM_jet_boue", (0.30, 0.07, 0.03), 0, 0.2)
M_J_HYD = mat("SIM_jet_hydrate", (0.92, 0.92, 0.90), 0, 0.2)
M_TUYAU = mat("SIM_tuyau_arrosage", (0.03, 0.20, 0.04), 0, 0.45)

# ================================================================== 1. ENTREE dans le broyeur (40-380)
# tambour + couvercle a charniere (cote arriere : il s'ouvre comme une porte)
e_fut = empty("SIM_fut", (X_A0, 0, ZD))
e_lid = empty("SIM_charniere_couvercle_fut", (X_A0 + 0.196, RD + 0.004, ZD))
adopt(e_lid, named("A0_couvercle"))
grille = []                                # grille de vidange (retient les billes)
for k in range(-3, 4):
    corde = 2 * math.sqrt(max(0.13 ** 2 - (k * 0.033) ** 2, 0.0))
    grille.append(box("SIM_grille_vidange", (0.004, 0.006, corde), (X_A0 + 0.185, k * 0.033, ZD), ns["M_TOLE"], sim))
    grille.append(box("SIM_grille_vidange", (0.004, corde, 0.006), (X_A0 + 0.185, 0, ZD + k * 0.033), ns["M_TOLE"], sim))
adopt(e_fut, named("A0_fut") + named("A0_charniere") + [e_lid] + grille)

for f, a in ((1, 0), (50, 0), (66, 115), (362, 115), (378, 0),
             (565, 0), (580, 115), (778, 115), (793, 0)):
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

# seau de bauxite brute (morceaux), avec anse et etiquettes
BX, BY = X_A0 - 0.14, -0.50
seau_b = lathe("SIM_seau_bauxite_brute", [(0, 0), (0.09, 0), (0.105, 0.17), (0.10, 0.17), (0.086, 0.004), (0, 0.004)],
               ns["M_NOIR"], sim, (BX, BY, 0))
tas = []
for i in range(18):
    a_ = rnd2.uniform(0, math.tau)
    rr_ = rnd2.uniform(0, 0.055)
    tas.append(caillou("SIM_bauxite_brute", (BX + rr_ * math.cos(a_), BY + rr_ * math.sin(a_),
                                             0.035 + (i // 6) * 0.05 + rnd2.uniform(0, 0.02)), rnd2.uniform(0.022, 0.034)))
et_seau = []
for az in (-55, 15):                       # deux etiquettes : une reste visible quand on verse
    et_seau += etiquette(f"SIM_seau_bauxite_etiquette_{az}", "BAUXITE", (BX, BY, 0), 0.09, 0.105, 0.17,
                         0.03, 0.15, 0.16, sim, taille=0.036, az=az)
adopt(seau_b, tas + et_seau + [anse("SIM_seau_bauxite_anse", (BX, BY, 0), 0.105, 0.17)])
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
bac_b = lathe("SIM_bac_billes", [(0, 0), (0.075, 0), (0.085, 0.09), (0.082, 0.09), (0.072, 0.003), (0, 0.003)],
              ns["M_TOLE"], sim, (TX, TY, 0))
tas_b = []
for i in range(10):
    a_ = rnd2.uniform(0, math.tau)
    rr_ = rnd2.uniform(0, 0.045)
    tas_b.append(bille("SIM_bille_tas", (TX + rr_ * math.cos(a_), TY + rr_ * math.sin(a_), 0.02 + (i // 5) * 0.025)))
et_bac = []
for az in (-55, 15):
    et_bac += etiquette(f"SIM_bac_billes_etiquette_{az}", "BILLES\nD'ACIER", (TX, TY, 0), 0.075, 0.085, 0.09,
                        0.01, 0.08, 0.13, sim, taille=0.022, az=az)
adopt(bac_b, tas_b + et_bac + [anse("SIM_bac_billes_anse", (TX, TY, 0), 0.085, 0.09)])
o_bac = P_TREMIE - bascule(0.085, 0.09)
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

# ================================================================== 3. VIDANGE (565-795) : grille, palan, fut incline
for ob in grille:
    visible(ob, 580, 776)
BAC = Vector((X_A0 + 0.65, -0.45, 0))
haut = 0.95
for f, p, ry in ((600, (X_A0, 0, ZD), 0), (615, (X_A0, 0, haut), 0), (635, (BAC.x, BAC.y, haut), 0),
                 (651, (BAC.x, BAC.y, haut), 90), (663, (BAC.x, BAC.y, 0.55), 90), (715, (BAC.x, BAC.y, 0.55), 90),
                 (727, (BAC.x, BAC.y, haut), 90), (743, (BAC.x, BAC.y, haut), 0), (763, (X_A0, 0, haut), 0),
                 (775, (X_A0, 0, ZD), 0)):
    kloc(e_fut, f, p)
    krot(e_fut, f, (ROT_FIN, rad(ry), 0))
flux("SIM_flux_poudre_vidange", [(BAC.x, BAC.y, 0.35), (BAC.x, BAC.y, 0.05)], 24, 665, 715, grain,
     periode=10, jitter=0.03)

e_bin = empty("SIM_bac_poudre", BAC)
poudre_bin = lathe("SIM_poudre_dans_bac", [(0, 0), (0.10, 0), (0.111, 0.11), (0, 0.11)], ns["M_BAUX"], sim,
                   (BAC.x, BAC.y, 0.004))
adopt(e_bin, named("A0_bac_poudre") + [poudre_bin, anse("SIM_bac_poudre_anse", BAC, 0.12, 0.22)]
      + etiquette("SIM_bac_poudre_etiquette_15", "POUDRE DE\nBAUXITE", BAC, 0.10, 0.12, 0.22,
                  0.04, 0.19, 0.19, sim, taille=0.030, az=15))
level(poudre_bin, ((1, 0), (667, 0), (715, 1.0), (1068, 1.0), (1110, 0)))

# ---- potence + palan : le crochet suit le fut pendant tout le levage
P = ns["POTENCE"]
pcx, pcy, zf = P["cx"], P["cy"], P["z_fleche"]
th0 = rad(P["angle0"])
u0 = Vector((math.cos(th0), math.sin(th0), 0))
trol0 = Vector((pcx, pcy, zf)) + u0 * P["d0"]
e_arm = empty("SIM_potence_fleche", (pcx, pcy, zf), (0, 0, th0))
e_trol = empty("SIM_potence_chariot", trol0)
e_hook = empty("SIM_potence_crochet", (trol0.x, trol0.y, P["z_crochet0"]))
adopt(e_hook, named("A0_potence_crochet") + named("A0_potence_etrier") + named("A0_potence_tourillon"))
adopt(e_trol, named("A0_potence_chariot") + named("A0_potence_palan") + named("A0_potence_chaine")
      + named("A0_potence_etiquette") + [e_hook])
adopt(e_arm, named("A0_potence_fleche") + named("A0_potence_tirant") + [e_trol])
chaine = D["A0_potence_chaine"]

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
ouvrir_trappe(e_t2, g2, 1660, 1850)
H1 = Vector((X_R1 + 0.125 * math.cos(rad(345)), 0.125 * math.sin(rad(345)), 0))
H2 = Vector((X_R2 - 0.125 * math.cos(rad(345)), 0.125 * math.sin(rad(345)), 0))

# 4a. l'eau arrive par un tuyau depuis le robinet (19 L)
rxr, ryr = X_R1 - 0.70, 0.35
tuyau_eau = hose("SIM_tuyau_eau", [(rxr, ryr - 0.06, 0.83), (rxr + 0.10, -0.30, 0.65), (X_R1 - 0.25, -0.42, 1.60),
                                   (H1.x, H1.y, 1.52), (H1.x, H1.y, 1.36)], 0.011, M_TUYAU, sim)
visible(tuyau_eau, 795, 880)
jet("SIM_jet_eau_R1", (H1.x, H1.y, 1.36), (H1.x, H1.y, Z0 + 0.01), 0.008, M_EAU, 805, 870)
e_rob = empty("SIM_manette_robinet", (rxr, ryr - 0.03, 0.885))
adopt(e_rob, [D["Robinet_manette"]])
for f, a in ((1, 0), (798, 0), (804, 90), (870, 90), (876, 0)):
    krot(e_rob, f, (0, 0, rad(a)))

# 4b. la soude (4,3 kg), versee dans l'eau par la trappe
P_R1 = Vector((H1.x, H1.y, 1.47))
SX, SY = X_R1 - 0.45, -0.62
pot = lathe("SIM_pot_soude", [(0, 0), (0.08, 0), (0.085, 0.15), (0.082, 0.15), (0.077, 0.004), (0, 0.004)],
            ns["M_BLANC"], sim, (SX, SY, 0))
tas_s = lathe("SIM_soude_paillettes", [(0, 0), (0.077, 0), (0.080, 0.11), (0, 0.11)], ns["M_BLANC"], sim, (SX, SY, 0.004))
et_pot = []
for az in (-55, 15):
    et_pot += etiquette(f"SIM_pot_soude_etiquette_{az}", "SOUDE\nNaOH", (SX, SY, 0), 0.08, 0.085, 0.15,
                        0.02, 0.135, 0.13, sim, taille=0.034, m_txt=ns["M_DANGER"], az=az)
adopt(pot, [tas_s, anse("SIM_pot_soude_anse", (SX, SY, 0), 0.085, 0.15)] + et_pot)
o_pot = P_R1 - bascule(0.085, 0.15)
porter(pot, [(1, (SX, SY, 0), (0, 0, 0)), (880, (SX, SY, 0), None), (892, (SX, SY, 1.66), None),
             (910, (o_pot.x, o_pot.y, 1.66), (0, 0, 0)), (914, o_pot, None), (924, o_pot, (rad(-110), 0, 0)),
             (960, o_pot, (rad(-110), 0, 0)), (968, o_pot, (0, 0, 0)), (972, (o_pot.x, o_pot.y, 1.66), None),
             (988, (SX, SY, 1.66), None), (1000, (SX, SY, 0), None)])
kscale(tas_s, 924, (1, 1, 1))
kscale(tas_s, 960, (1, 1, 0.03))
flux("SIM_flux_soude", [P_R1, (H1.x, H1.y, 1.30), (H1.x, H1.y, 1.07)], 10, 924, 962, flocon, periode=14, jitter=0.008)

# 4c. la poudre de bauxite : le bac est porte du broyeur jusqu'a la trappe
o_bin = P_R1 - bascule(0.12, 0.22)
DEPOT = (X_R1 - 0.20, -0.62, 0)
porter(e_bin, [(1, BAC, (0, 0, 0)), (1000, BAC, None), (1015, (BAC.x, BAC.y, 1.72), None),
               (1045, (o_bin.x, o_bin.y, 1.72), (0, 0, 0)), (1050, o_bin, None), (1062, o_bin, (rad(-110), 0, 0)),
               (1110, o_bin, (rad(-110), 0, 0)), (1118, o_bin, (0, 0, 0)), (1124, (o_bin.x, o_bin.y, 1.72), None),
               (1140, (DEPOT[0], DEPOT[1], 1.72), None), (1155, DEPOT, None)])
flux("SIM_flux_poudre_R1", [P_R1, (H1.x, H1.y, 1.30), (H1.x, H1.y, 1.10)], 22, 1064, 1110, grain,
     periode=10, jitter=0.012)

liq1 = D["R1_Attaque_liquide"]
liq1.location.z += 0.0005
m1 = liq1.data.materials[0]
level(liq1, ((1, 0), (805, 0), (870, 0.68), (924, 0.68), (960, 0.75), (1064, 0.75), (1110, 0.84),
             (1420, 0.84), (1500, 0.30), (1520, 0.30), (1580, 0)))
for f, (rgb, a) in ((805, EAU), (1064, EAU), (1110, PULPE), (1330, PULPE), (1410, AMBRE)):
    kmat(m1, f, rgb, a)


def agitateur(tag, X, f0, f1):
    e = empty("SIM_rot_" + tag, (X, 0, 1.0))
    adopt(e, named(tag + "_arbre") + named(tag + "_moyeu") + named(tag + "_pale") + named(tag + "_accouplement"))
    spin(e, f0, f1, 2, 9)


agitateur("R1_Attaque", X_R1, 900, 1330)
agitateur("R2_Precipitation", X_R2, 1800, 2010)
agiter_liquide(m1, 900, 1330)

# temperatures affichees par les regulateurs de R1 et R2
afficheur(D["R1_Attaque_afficheur_PV"],
          ((1, "25"), (930, "62"), (1000, "58"), (1110, "70"), (1150, "88"), (1175, "100"), (1330, "97"),
           (1380, "92"), (1420, "88"), (1520, "85"), (1600, "60"), (1700, "40")))
afficheur(D["R2_Precipitation_afficheur_PV"],
          ((1, "25"), (1690, "84"), (1760, "78"), (1830, "66"), (1880, "60"), (1940, "55"), (1990, "50"),
           (2110, "45")))

# ================================================================== 5-6. ATTAQUE puis DECANTATION dans R1
boue1 = lathe("SIM_boue_decantee", [(0, 0), (0.1965, 0), (0.1965, 0.045), (0, 0.045)],
              ns["M_BOUE"], sim, (X_R1, 0, Z0 + 0.007), -45.6, 271.2)
level(boue1, ((1, 0), (1330, 0), (1410, 1), (1520, 1), (1580, 0)))

# ================================================================== 7. FILTRATION de R1 par les vannes (vide limite)
def vanne(tag, nom, x, y, z, f_open, f_close):
    e = empty(f"SIM_rot_vanne_{tag}_{nom}", (x, y, z))
    adopt(e, [D[f"{tag}_poignee_{nom}"]])
    for f, a in ((1, 0), (f_open, 0), (f_open + 10, 90), (f_close, 90), (f_close + 10, 0)):
        krot(e, f, (0, 0, rad(a)), 'LINEAR')


sx, sy = 0.335 * math.cos(rad(15)), 0.335 * math.sin(rad(15))
vanne("R1_Attaque", "haute", X_R1 + sx, sy, Z0 + 0.075, 1410, 1500)
vanne("R1_Attaque", "basse", X_R1 + sx, -sy, Z0 + 0.022, 1510, 1580)
vanne("R2_Precipitation", "basse", X_R2 - sx, -sy, Z0 + 0.022, 2010, 2100)

jet("SIM_jet_liqueur", (-0.11, 0.03, 0.83), (-0.11, 0.03, 0.56), 0.011, M_J_AMBRE, 1420, 1500)
jet("SIM_jet_boue", (-0.11, -0.03, 0.83), (-0.11, -0.03, 0.56), 0.013, M_J_BOUE, 1520, 1580)
jet("SIM_jet_hydrate", (0.11, -0.03, 0.83), (0.11, -0.03, 0.56), 0.013, M_J_HYD, 2020, 2100)

M_FILTRAT = mat("SIM_mat_filtrat", AMBRE[0], 0, 0.3, alpha=AMBRE[1])
filtrat = lathe("SIM_filtrat_dans_fut", [(0, 0), (0.169, 0), (0.187, 0.028), (0.187, 0.26), (0, 0.26)],
                M_FILTRAT, sim, (X_F, 0, 0.0435), -45, 270)
level(filtrat, ((1, 0), (1420, 0), (1500, 0.65), (1520, 0.65), (1580, 0.80), (1685, 0.80), (1760, 0),
                (2020, 0), (2100, 0.9)))
kmat(M_FILTRAT, 1, *AMBRE, kind='CONSTANT')
kmat(M_FILTRAT, 1770, *PALE, kind='CONSTANT')

# manometre de la pompe a vide : vide faible (-0,2 bar) pour la liqueur chaude, plus fort pour l'hydrate tiede
axe = D["F_pompe_axe_aiguille"]
e_aig = empty("SIM_rot_aiguille", axe.location.copy())
adopt(e_aig, [D["F_pompe_aiguille"]])
for f, a in ((1, -75), (1410, -75), (1430, -45), (1580, -45), (1600, -75), (2010, -75), (2030, 0),
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
etiquette("SIM_bac_boues_etiquette", "BOUES\nROUGES", (-0.55, -0.85, 0), 0.19, 0.21, 0.18, 0.025, 0.16, 0.30,
          sim, taille=0.045, az=-80)
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
jet("SIM_jet_liqueur_R2", (H2.x, H2.y, 1.36), (H2.x, H2.y, Z0 + 0.01), 0.009, M_J_AMBRE, 1685, 1760)
liq2 = D["R2_Precipitation_liquide"]
liq2.location.z += 0.0005
m2 = liq2.data.materials[0]
level(liq2, ((1, 0), (1685, 0), (1760, 0.82), (1819, 0.82), (1845, 0.86), (2020, 0.86), (2100, 0)))
for f, (rgb, a) in ((1685, AMBRE), (1830, AMBRE), (1990, LAIT)):
    kmat(m2, f, rgb, a)
agiter_liquide(m2, 1800, 2010)

# ================================================================== 10. PRECIPITATION PAR AMORCAGE (1775-2010)
# pot d'amorce (hydrate d'un lot precedent) verse par la trappe de R2, puis 48 h de 60 a 50 degres
AX, AY = X_R2 + 0.45, -0.62
P_R2 = Vector((H2.x, H2.y, 1.47))
pot_a = lathe("SIM_pot_amorce", [(0, 0), (0.08, 0), (0.085, 0.15), (0.082, 0.15), (0.077, 0.004), (0, 0.004)],
              ns["M_COFFRET"], sim, (AX, AY, 0))
tas_a = lathe("SIM_amorce_hydrate", [(0, 0), (0.077, 0), (0.080, 0.10), (0, 0.10)], ns["M_BLANC"], sim, (AX, AY, 0.004))
et_am = []
for az in (-55, 15):
    et_am += etiquette(f"SIM_pot_amorce_etiquette_{az}", "AMORCE\nAl(OH)3", (AX, AY, 0), 0.08, 0.085, 0.15,
                       0.02, 0.135, 0.13, sim, taille=0.026, az=az)
adopt(pot_a, [tas_a, anse("SIM_pot_amorce_anse", (AX, AY, 0), 0.085, 0.15)] + et_am)
o_pa = P_R2 - bascule(0.085, 0.15)
porter(pot_a, [(1, (AX, AY, 0), (0, 0, 0)), (1775, (AX, AY, 0), None), (1787, (AX, AY, 1.66), None),
               (1805, (o_pa.x, o_pa.y, 1.66), (0, 0, 0)), (1809, o_pa, None), (1819, o_pa, (rad(-110), 0, 0)),
               (1845, o_pa, (rad(-110), 0, 0)), (1853, o_pa, (0, 0, 0)), (1857, (o_pa.x, o_pa.y, 1.66), None),
               (1871, (AX, AY, 1.66), None), (1883, (AX, AY, 0), None)])
kscale(tas_a, 1819, (1, 1, 1))
kscale(tas_a, 1845, (1, 1, 0.03))
kscale(tas_a, 2170, (1, 1, 0.03))
kscale(tas_a, 2180, (1, 1, 0.6))           # une partie du nouvel hydrate revient dans le pot
flux("SIM_flux_amorce", [P_R2, (H2.x, H2.y, 1.30), (H2.x, H2.y, 1.12)], 18, 1819, 1845, grain_blanc,
     periode=10, jitter=0.012)

# ================================================================== 11. FILTRATION de l'hydrate, amorce gardee, creusets
hyd = lathe("SIM_gateau_hydrate", [(0, 0), (0.162, 0), (0.162, 0.05), (0, 0.05)],
            ns["M_BLANC"], sim, (X_F, 0, 0.553))
level(hyd, ((1, 0), (2020, 0), (2100, 1)))

xcK, ycK = X_K - 0.08, -0.08               # centre de la chambre du four
TABLE = Vector((X_K + 0.60, -0.10, 0.628))  # creusets en attente sur la table de preparation
porter(hyd, [(2120, (X_F, 0, 0.553), None), (2135, (X_F, 0, 1.05), None), (2150, (0.30, -0.62, 1.05), None),
             (2160, (AX, AY, 1.05), None), (2168, (AX, AY, 1.05), None),
             (2188, (TABLE.x, -0.62, 1.05), None), (2196, (TABLE.x, TABLE.y, 1.05), None),
             (2206, (TABLE.x, TABLE.y, TABLE.z + 0.15), None)])
kscale(hyd, 2160, (1, 1, 1))
kscale(hyd, 2168, (0.58, 0.58, 1))         # ~3,5 kg reviennent a l'amorce, ~1,7 kg continuent
kscale(hyd, 2196, (0.58, 0.58, 1))
kscale(hyd, 2206, (0.42, 0.42, 0.42))
kscale(hyd, 2207, 0, 'CONSTANT')
part = lathe("SIM_part_amorce", [(0, 0), (0.075, 0), (0.075, 0.05), (0, 0.05)], ns["M_BLANC"], sim, (AX, AY, 1.05))
visible(part, 2161, 2176)
porter(part, [(2161, (AX, AY, 1.05), None), (2176, (AX, AY, 0.08), None)])

# 3 creusets empiles sur une plaque d'enfournement ; un empty porte l'ensemble (table -> four -> table)
e_gaz = empty("SIM_creusets", (xcK, ycK, 0.628))
alus = named("K_alumine")
for alu in alus:
    h = alu.dimensions.z / 2
    alu.data.transform(Matrix.Translation((0, 0, h)))
    alu.location.z -= h
adopt(e_gaz, named("K_gazette") + alus)
for alu in alus:
    kscale(alu, 1, 0, 'CONSTANT')
    kscale(alu, 2206, 1, 'LINEAR')
    kscale(alu, 2300, (1, 1, 1), 'LINEAR')
    kscale(alu, 2370, (1, 1, 0.65), 'LINEAR')    # perte de masse : l'eau part

# ================================================================== 12. les creusets entrent PAR LA PORTE, a plat
DEVANT = (xcK, -0.62, 0.64)
porter(e_gaz, [(1, TABLE, None), (2210, TABLE, None), (2216, (TABLE.x, TABLE.y, 0.64), None),
               (2236, DEVANT, None), (2256, (xcK, ycK, 0.64), None), (2262, (xcK, ycK, 0.628), None),
               (2420, (xcK, ycK, 0.628), None), (2426, (xcK, ycK, 0.64), None), (2444, DEVANT, None),
               (2462, (TABLE.x, TABLE.y, 0.64), None), (2468, TABLE, None)])
for ob in etiquette("SIM_chevalet_alumine", "ALUMINE\nAl2O3", (TABLE.x, TABLE.y - 0.14, TABLE.z), 0.0, 0.0, 1.0,
                    0.0, 0.10, 0.18, sim, taille=0.036, az=-80, plat=True):
    visible(ob, 2468)

# ================================================================== 13-14. CALCINATION et REFROIDISSEMENT
e_porte = empty("SIM_rot_porte", (X_K - 0.28, -0.23, 0.80))
adopt(e_porte, named("K_porte") + named("K_poignee_porte"))
for f, a in ((1, 0), (2265, 0), (2290, 100), (2395, 100), (2415, 0)):
    krot(e_porte, f, (0, 0, rad(a)))

afficheur(D["K_afficheur_PV"],
          ((1, "25"), (2292, "150"), (2302, "290"), (2312, "400"), (2330, "400"), (2338, "560"), (2346, "780"),
           (2352, "960"), (2358, "1050"), (2374, "820"), (2380, "540"), (2386, "260"), (2392, "95"), (2420, "60")))

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
# cadrage : objectif un peu plus large et image decalee vers le haut, pour laisser en bas
# un bandeau noir reserve aux legendes, qui ne recouvre que le sol
cam.data.lens = 28
cam.data.shift_y = -0.0565
cam.data.clip_start = 0.05
cible = empty("SIM_cible_camera", (0.05, 0, 0.85))
con = cam.constraints.new('TRACK_TO')
con.target = cible
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
plans = (
    ((1, 30),       (0.4, -7.7, 2.9),     (0.05, 0, 0.85)),       # vue d'ensemble
    ((58, 372),     (-0.95, -2.55, 1.60), (-2.00, -0.22, 0.60)),  # entree dans le broyeur
    ((392, 788),    (-0.85, -2.85, 1.65), (-1.95, -0.10, 0.80)),  # broyage + vidange au palan
    ((805, 1160),   (-0.15, -3.15, 2.10), (-1.10, -0.25, 1.00)),  # chargement de R1
    ((1175, 1400),  (-0.55, -2.50, 1.75), (-0.85, 0.00, 1.10)),   # attaque, decantation
    ((1415, 1655),  (-0.35, -3.20, 1.65), (-0.40, -0.25, 0.60)),  # filtration, boue rouge
    ((1668, 2110),  (0.80, -3.45, 2.15),  (0.70, -0.20, 0.95)),   # transfert, amorcage, filtration
    ((2125, 2205),  (1.55, -3.90, 2.00),  (1.55, -0.25, 0.80)),   # hydrate -> amorce + creusets
    ((2212, 2445),  (2.90, -2.15, 1.35),  (2.68, -0.20, 0.72)),   # four
    ((2470, 2520),  (3.30, -1.55, 1.25),  (2.95, -0.10, 0.65)),   # alumine sur la table
)
for (fa, fb), pc, pt in plans:
    for f in (fa, fb):
        kloc(cam, f, pc)
        kloc(cible, f, pt)

# ================================================================== LEGENDES, HORLOGE, MENTION "VUE EN COUPE"
M_HUD = mat("SIM_texte_ecran", (1, 1, 1), 0, 0.5, emit=1.5)
M_HUD_J = mat("SIM_texte_horloge", (1.0, 0.75, 0.2), 0, 0.5, emit=1.5)
M_BANDE = mat("SIM_bandeau", (0.012, 0.012, 0.015), 0, 1.0)
M_PASTILLE = mat("SIM_pastille", (0.012, 0.012, 0.015), 0, 1.0, alpha=0.75)
DH = 0.3                                   # distance du bandeau a la camera (rien ne passe devant)
YB = -0.3917 * DH                          # centre du bandeau : tout en bas de l'image
YH = 0.255 * DH                            # haut de l'image (pastilles)
hud = []
bande = box("SIM_bandeau", (1.32 * DH, 0.086 * DH, 0.0005), (0, 0, 0), M_BANDE, sim)
bande.parent = cam
bande.location = (0, YB, -DH - 0.002)
hud.append(bande)


def texte_hud(nom, txt, x, y, taille, m, f0, f1=None, align='CENTER'):
    cu = bpy.data.curves.new(nom, 'FONT')
    cu.body = txt
    cu.size = taille * DH
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.materials.append(m)
    ob = bpy.data.objects.new(nom, cu)
    sim.objects.link(ob)
    ob.parent = cam
    ob.location = (x * DH, y, -DH)
    visible(ob, f0, f1)
    hud.append(ob)
    return ob


def pastille(nom, x, larg, f0, f1=None):
    ob = box(nom, (larg * DH, 0.05 * DH, 0.0005), (0, 0, 0), M_PASTILLE, sim)
    ob.parent = cam
    ob.location = (x * DH, YH, -DH - 0.002)
    visible(ob, f0, f1)
    hud.append(ob)


legendes = (
    (1,    "De la bauxite à l'alumine  -  premier lot : 5 kg de bauxite"),
    (40,   "1. ENTRÉE  -  on ouvre le fût, le chariot à trémie s'avance"),
    (130,  "5 kg de bauxite brute versés dans la trémie, ils glissent dans le fût"),
    (250,  "Puis les billes d'acier ; le chariot recule, on referme le fût"),
    (380,  "2. BROYAGE  -  la bauxite est réduite en poudre (< 250 µm)"),
    (565,  "3. VIDANGE  -  grille posée, le palan lève et incline le fût"),
    (650,  "La grille retient les billes, la poudre tombe dans le bac"),
    (780,  "4. CHARGEMENT de R1  -  19 L d'eau par la trappe"),
    (880,  "Puis 4,3 kg de soude, toujours versée dans l'eau"),
    (1000, "Puis les 5 kg de poudre de bauxite"),
    (1170, "5. ATTAQUE  -  100 °C, 2 h : l'alumine se dissout dans la soude"),
    (1330, "6. DÉCANTATION  -  les boues rouges tombent au fond"),
    (1410, "7. FILTRATION  -  vide faible (-0,2 bar) : la liqueur chaude ne bout pas"),
    (1510, "Vanne basse : les boues rouges restent sur la toile"),
    (1590, "La galette de boue rouge est sortie par le haut du filtre"),
    (1660, "8. TRANSFERT  -  pompe : la liqueur entre dans R2 par la trappe"),
    (1775, "9. PRÉCIPITATION  -  on ajoute l'amorce d'hydrate"),
    (1860, "Agitation 48 h en refroidissant de 60 à 50 °C : l'hydrate se forme"),
    (2010, "10. FILTRATION  -  l'hydrate d'alumine reste sur la toile"),
    (2070, "La liqueur épuisée est gardée : elle repart à l'attaque du lot suivant"),
    (2115, "11. Environ 3,5 kg d'hydrate retournent dans le pot d'amorce"),
    (2178, "Le reste (environ 1,7 kg) va dans les creusets"),
    (2208, "12. Les creusets entrent dans le four par la porte"),
    (2266, "13. CALCINATION  -  palier à 400 °C, puis 1050 °C : l'eau part"),
    (2366, "14. REFROIDISSEMENT  -  porte fermée jusqu'à moins de 100 °C"),
    (2420, "ALUMINE  -  environ 1,1 kg ; le reste repart avec la liqueur"),
)
for i, (f0, txt) in enumerate(legendes):
    f1 = legendes[i + 1][0] if i + 1 < len(legendes) else None
    texte_hud(f"SIM_legende_{i:02d}", txt, 0, YB, 0.032, M_HUD, f0, f1)

# horloge : duree reelle de chaque etape (le film va beaucoup plus vite que la realite)
horloge = (
    (40, "Durée réelle : 10 min"), (380, "Durée réelle : 1 à 2 h"), (565, "Durée réelle : 15 min"),
    (780, "Durée réelle : 30 min"), (1170, "Durée réelle : 2 h"), (1330, "Durée réelle : 1 à 2 h"),
    (1410, "Durée réelle : 1 h"), (1660, "Durée réelle : 15 min"), (1775, "Durée réelle : 48 h"),
    (2010, "Durée réelle : 1 h"), (2115, "Puis séchage : 1 nuit à 110 °C"), (2208, "Durée réelle : 5 min"),
    (2266, "Durée réelle : environ 6 h"), (2366, "Durée réelle : 1 nuit"), (2420, "Un lot : environ 4 jours"),
)
pastille("SIM_pastille_horloge", 0.43, 0.40, 40)
for i, (f0, txt) in enumerate(horloge):
    f1 = horloge[i + 1][0] if i + 1 < len(horloge) else None
    texte_hud(f"SIM_horloge_{i:02d}", txt, 0.43, YH, 0.024, M_HUD_J, f0, f1)

# mention permanente : les cuves et le filtre sont montres en coupe
pastille("SIM_pastille_coupe", -0.43, 0.40, 40)
texte_hud("SIM_mention_coupe", "Vue en coupe : cuves et filtre ouverts", -0.43, YH, 0.020, M_HUD, 40)

for ob in hud:                              # ni ombre ni reflet dans les metaux
    for p in ("visible_shadow", "visible_glossy", "visible_diffuse", "visible_transmission", "visible_volume_scatter"):
        if hasattr(ob, p):
            setattr(ob, p, False)

apply_interpolations()

# ================================================================== PALAN : images cles calculees image par image
def lisse(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


GARE = Vector((trol0.x, trol0.y, P["z_crochet0"]))
DESSUS = Vector((X_A0, 0, 1.30))
ACCROCHE = Vector((X_A0, 0, ZD + 0.30))
pts_crochet = {}
for f in range(560, 811):
    if f < 590:
        H = GARE.lerp(DESSUS, lisse((f - 560) / 30))
    elif f < 600:
        H = DESSUS.lerp(ACCROCHE, lisse((f - 590) / 10))
    elif f <= 775:
        sc.frame_set(f)
        H = e_fut.matrix_world.translation.copy() + Vector((0, 0, 0.30))
    elif f < 785:
        H = ACCROCHE.lerp(DESSUS, lisse((f - 775) / 10))
    else:
        H = DESSUS.lerp(GARE, lisse((f - 785) / 25))
    pts_crochet[f] = H
prev = th0
for f in range(560, 811):
    H = pts_crochet[f]
    th = math.atan2(H.y - pcy, H.x - pcx)
    while th - prev > math.pi:
        th -= math.tau
    while th - prev < -math.pi:
        th += math.tau
    prev = th
    d = math.hypot(H.x - pcx, H.y - pcy)
    krot(e_arm, f, (0, 0, th), 'LINEAR')
    kloc(e_trol, f, (pcx + u0.x * d, pcy + u0.y * d, zf), 'LINEAR')
    kloc(e_hook, f, (trol0.x, trol0.y, H.z), 'LINEAR')
    krot(e_hook, f, (0, 0, -(th - th0)), 'LINEAR')
    kscale(chaine, f, (1, 1, P["z_chaine"] - (H.z + 0.05)), 'LINEAR')
apply_interpolations()

# liquides semi-transparents : melange lisse plutot que tramage (sinon effet granuleux)
for m in (m1, m2, M_FILTRAT, M_J_AMBRE, M_VAPEUR, M_EAU, M_PASTILLE):
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
