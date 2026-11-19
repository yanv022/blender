# Animation du procede bauxite -> alumine (60 s a 24 images/s), sur le modele realiste.
# Reconstruit la scene (construire_usine.py + materiaux_realistes.py) puis ajoute les images cles.
# A lancer depuis Blender (onglet Scripting) ; les deux autres scripts doivent etre dans le meme dossier.

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
sc.frame_start, sc.frame_end = 1, 1440
sc.render.fps = 24
sim = coll("SIM_Animation")
rad = math.radians

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
                if kind:
                    kp.interpolation = kind
            fc.update()

def kloc(ob, f, loc, kind='BEZIER'):
    ob.location = loc
    ob.keyframe_insert("location", frame=f)
    reg(ob, "location", f, kind)

def kscale(ob, f, s, kind='LINEAR'):
    ob.scale = (s, s, s) if isinstance(s, (int, float)) else s
    ob.keyframe_insert("scale", frame=f)
    reg(ob, "scale", f, kind)

def krot(ob, f, e, kind='LINEAR'):
    ob.rotation_euler = e
    ob.keyframe_insert("rotation_euler", frame=f)
    reg(ob, "rotation_euler", f, kind)

def level(ob, pairs):
    """Niveau d'un liquide ou d'un gateau : echelle Z, objet cache quand il est vide."""
    n = len(pairs)
    for i, (f, s) in enumerate(pairs):
        nxt = pairs[i + 1][1] if i + 1 < n else s
        prv = pairs[i - 1][1] if i > 0 else 0
        if s > 0:
            kscale(ob, f, (1, 1, s), 'LINEAR')
        elif nxt > 0:                       # debut de remplissage
            if f > 1:
                kscale(ob, f - 1, 0, 'CONSTANT')
            kscale(ob, f, (1, 1, 0.002), 'LINEAR')
        elif prv > 0:                       # fin de vidange
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

def empty(name, loc):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
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
    krot(ob, f0, e0)
    krot(ob, f1, e1)

EAU    = ((0.60, 0.80, 0.95), 0.35)
PULPE  = ((0.40, 0.10, 0.05), 0.96)
AMBRE  = ((0.85, 0.55, 0.15), 0.50)
LAIT   = ((0.96, 0.96, 0.95), 0.96)
PALE   = ((0.75, 0.86, 0.92), 0.40)

# ================================================================== 1. BROYAGE (40-200)
ZD = 0.625
e_fut = empty("SIM_rot_fut", (X_A0, 0, ZD))
e_lid = empty("SIM_couvercle_fut", (X_A0 + 0.205, 0, ZD))      # couvercle amovible (chargement)
adopt(e_lid, named("A0_couvercle") + named("A0_cercle") + named("A0_levier"))
adopt(e_fut, named("A0_fut") + named("A0_bourrelet") + [e_lid])
spin(e_fut, 40, 200, 0, -8)

# ================================================================== 2. CHARGEMENT de R1 (200-290)
Z0 = 0.90
seau = lathe("SIM_seau", [(0, 0), (0.09, 0), (0.10, 0.16), (0.097, 0.16), (0.087, 0.003), (0, 0.003)],
             ns["M_COFFRET"], sim, (X_A0 + 0.12, -0.50, 0.0))
poudre = lathe("SIM_poudre_bauxite", [(0, 0), (0.087, 0), (0.094, 0.12), (0, 0.12)],
               ns["M_BAUX"], sim, (X_A0 + 0.12, -0.50, 0.003))
adopt(seau, [poudre])
kscale(seau, 1, 0, 'CONSTANT')
kscale(seau, 200, 0, 'LINEAR')
kscale(seau, 206, 1, 'CONSTANT')
kscale(seau, 296, 0, 'CONSTANT')
kloc(seau, 206, (X_A0 + 0.12, -0.50, 0.0))
kloc(seau, 228, (-1.6, -0.75, 1.75))
kloc(seau, 250, (X_R1 + 0.121, -0.25, 1.55))
krot(seau, 252, (0, 0, 0), 'BEZIER')
krot(seau, 264, (rad(-110), 0, 0), 'BEZIER')
krot(seau, 286, (rad(-110), 0, 0), 'BEZIER')
krot(seau, 294, (0, 0, 0), 'BEZIER')
kscale(poudre, 262, (1, 1, 1))
kscale(poudre, 286, (1, 1, 0.02))
jet_p = rod("SIM_jet_poudre", (X_R1 + 0.121, -0.09, 1.48), (X_R1 + 0.121, -0.035, 1.335), 0.014, ns["M_BAUX"], sim)
visible(jet_p, 264, 286)

# ================================================================== 3-4. ATTAQUE et DECANTATION dans R1
liq1 = D["R1_Attaque_liquide"]
liq1.location.z += 0.0005            # evite le scintillement avec le fond de cuve
m1 = liq1.data.materials[0]
level(liq1, ((1, 0), (200, 0), (240, 0.57), (255, 0.57), (290, 0.65), (505, 0.65), (520, 0.93),
             (610, 0.93), (690, 0.30), (710, 0.30), (770, 0)))
for f, (rgb, a) in ((200, EAU), (255, EAU), (290, PULPE), (520, PULPE), (600, AMBRE)):
    kmat(m1, f, rgb, a)

boue1 = lathe("SIM_boue_decantee", [(0, 0), (0.1965, 0), (0.1965, 0.045), (0, 0.045)],
              ns["M_BOUE"], sim, (X_R1, 0, Z0 + 0.007), -45.6, 271.2)
level(boue1, ((1, 0), (520, 0), (600, 1), (710, 1), (770, 0)))

def agitateur(tag, X, f0, f1):
    e = empty("SIM_rot_" + tag, (X, 0, 1.0))
    adopt(e, named(tag + "_arbre") + named(tag + "_moyeu") + named(tag + "_pale") + named(tag + "_accouplement"))
    spin(e, f0, f1, 2, 9)

agitateur("R1_Attaque", X_R1, 215, 520)
agitateur("R2_Precipitation", X_R2, 860, 1080)

# ================================================================== 5-6. FILTRATION de R1 (600-780)
def vanne(tag, nom, x, y, z, f_open, f_close):
    e = empty(f"SIM_rot_vanne_{tag}_{nom}", (x, y, z))
    adopt(e, [D[f"{tag}_poignee_{nom}"]])
    krot(e, 1, (0, 0, 0))
    krot(e, f_open, (0, 0, 0))
    krot(e, f_open + 10, (0, 0, rad(90)))
    krot(e, f_close, (0, 0, rad(90)))
    krot(e, f_close + 10, (0, 0, 0))

sx, sy = 0.335 * math.cos(rad(15)), 0.335 * math.sin(rad(15))
vanne("R1_Attaque", "haute", X_R1 + sx, sy, Z0 + 0.075, 600, 690)
vanne("R1_Attaque", "basse", X_R1 + sx, -sy, Z0 + 0.022, 700, 770)
vanne("R2_Precipitation", "basse", X_R2 - sx, -sy, Z0 + 0.022, 1080, 1180)

M_J_AMBRE = mat("SIM_jet_ambre", AMBRE[0], 0, 0.2, alpha=0.8)
jet1 = rod("SIM_jet_liqueur", (-0.11, 0.03, 0.83), (-0.11, 0.03, 0.56), 0.012, M_J_AMBRE, sim)
visible(jet1, 610, 690)
jet2 = rod("SIM_jet_boue", (-0.11, -0.03, 0.83), (-0.11, -0.03, 0.56), 0.014, ns["M_BOUE"], sim)
visible(jet2, 710, 770)
jet3 = rod("SIM_jet_hydrate", (0.11, -0.03, 0.83), (0.11, -0.03, 0.56), 0.014, ns["M_BLANC"], sim)
visible(jet3, 1090, 1180)

M_FILTRAT = mat("SIM_mat_filtrat", AMBRE[0], 0, 0.3, alpha=AMBRE[1])
filtrat = lathe("SIM_filtrat_dans_fut", [(0, 0), (0.169, 0), (0.187, 0.028), (0.187, 0.26), (0, 0.26)],
                M_FILTRAT, sim, (X_F, 0, 0.0435), -45, 270)
level(filtrat, ((1, 0), (610, 0), (690, 0.65), (710, 0.65), (770, 0.80), (795, 0.80), (855, 0),
                (1090, 0), (1180, 0.9)))
kmat(M_FILTRAT, 1, *AMBRE, kind='CONSTANT')
kmat(M_FILTRAT, 870, *PALE, kind='CONSTANT')

for o in named("F_gateau_boue_rouge"):
    bpy.data.objects.remove(o)
gat_b = lathe("SIM_gateau_boue_rouge", [(0, 0), (0.162, 0), (0.162, 0.032), (0, 0.032)],
              ns["M_BOUE"], sim, (X_F, 0, 0.553))
level(gat_b, ((1, 0), (710, 0), (775, 1)))
# evacuation des boues vers un bac
lathe("SIM_bac_boues_rouges", [(0, 0), (0.19, 0), (0.21, 0.18), (0.205, 0.18), (0.186, 0.004), (0, 0.004)],
      ns["M_BAC"], sim, (-0.55, -0.85, 0))
kloc(gat_b, 790, (X_F, 0, 0.553))
kloc(gat_b, 815, (-0.25, -0.45, 1.05))
kloc(gat_b, 840, (-0.55, -0.85, 0.03))

# ================================================================== 7. TRANSFERT vers R2 (780-860)
tuyau = hose("SIM_tuyau_transfert",
             [(0.19, 0.0, 0.25), (0.42, -0.14, 0.95), (0.60, -0.08, 1.48), (X_R2 - 0.121, -0.032, 1.34)],
             0.010, ns["M_NOIR"], sim)
visible(tuyau, 785, 862)
liq2 = D["R2_Precipitation_liquide"]
liq2.location.z += 0.0005
m2 = liq2.data.materials[0]
level(liq2, ((1, 0), (795, 0), (855, 1.0), (1090, 1.0), (1180, 0)))
for f, (rgb, a) in ((795, AMBRE), (880, AMBRE), (1060, LAIT)):
    kmat(m2, f, rgb, a)

# ================================================================== 8. PRECIPITATION au CO2 (860-1080)
M_BULLE = mat("SIM_bulle_CO2", (1, 1, 1), 0, 0.1, emit=0.6)
rnd = random.Random(3)
zb, zt = Z0 + 0.04, Z0 + 0.225
for i in range(34):
    if i < 14:                      # bulles sur les faces de coupe, bien visibles
        th = 224.0 if i % 2 else 316.0
        r = rnd.uniform(0.03, 0.18)
    else:
        th = rnd.uniform(-40, 220)
        r = rnd.uniform(0.04, 0.17)
    x, y = X_R2 + r * math.cos(rad(th)), r * math.sin(rad(th))
    b = ball("SIM_bulle", rnd.uniform(0.005, 0.009), (x, y, zb), M_BULLE, sim)
    visible(b, 862, 1080)
    f = 860 + rnd.randint(0, 25)
    while f < 1080:
        p = rnd.randint(20, 32)
        kloc(b, f, (x, y, zb), 'LINEAR')
        kloc(b, f + p - 1, (x + rnd.uniform(-0.01, 0.01), y, zt), 'CONSTANT')
        f += p

# ================================================================== 9. FILTRATION de l'hydrate (1080-1200)
hyd = lathe("SIM_gateau_hydrate", [(0, 0), (0.162, 0), (0.162, 0.05), (0, 0.05)],
            ns["M_BLANC"], sim, (X_F, 0, 0.553))
level(hyd, ((1, 0), (1090, 0), (1180, 1), (1200, 1)))
kscale(hyd, 1258, (0.5, 0.5, 0.5), 'CONSTANT')
kscale(hyd, 1260, 0, 'CONSTANT')

# ================================================================== 10-12. FOUR (1200-1440)
xcK, ycK = X_K - 0.08, -0.08               # centre de la chambre du four
kloc(hyd, 1200, (X_F, 0, 0.553))
kloc(hyd, 1230, (1.25, -0.95, 1.25))
kloc(hyd, 1258, (xcK, ycK, 0.64))
kscale(hyd, 1258, (0.42, 0.42, 0.42), 'CONSTANT')

alu = D["K_alumine"]
h = alu.dimensions.z / 2
alu.data.transform(Matrix.Translation((0, 0, h)))          # origine au fond de la couche
alu.location.z -= h
kscale(alu, 1, 0, 'CONSTANT')
kscale(alu, 1260, 1, 'LINEAR')
kscale(alu, 1290, (1, 1, 1), 'LINEAR')
kscale(alu, 1370, (1, 1, 0.65), 'LINEAR')                  # perte de masse : l'eau part

# porte : modelisee ouverte a 100 degres, l'empty la referme autour de sa charniere
e_porte = empty("SIM_rot_porte", (X_K - 0.28, -0.23, 0.80))
adopt(e_porte, named("K_porte") + named("K_poignee_porte"))
for f, a in ((1, 0), (1262, 0), (1290, 100), (1388, 100), (1410, 0)):
    krot(e_porte, f, (0, 0, rad(a)), 'BEZIER')

# afficheur de temperature : une copie du texte par valeur, affichee a tour de role
pv = D["K_afficheur_PV"]
seq = ((1, "25"), (1292, "150"), (1302, "290"), (1312, "400"), (1330, "560"), (1340, "780"),
       (1350, "960"), (1358, "1050"), (1372, "820"), (1378, "540"), (1384, "260"), (1390, "95"),
       (1414, "60"))
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

def kemission(m, f, v):
    entree = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]
    entree.default_value = v
    entree.keyframe_insert("default_value", frame=f)
    reg(m.node_tree, None, f, 'CONSTANT')

m_vc = mat("SIM_voyant_chauffe", (0.6, 0.02, 0.01), 0, 0.3, emit=4.0)
D["K_voyant_chauffe"].data.materials[0] = m_vc
for f, v in ((1, 0.0), (1292, 4.0), (1360, 0.0)):
    kemission(m_vc, f, v)

M_VAPEUR = mat("SIM_vapeur", (1, 1, 1), 0, 0.9, alpha=0.5)
for i in range(7):
    v = ball("SIM_vapeur", 0.02, (xcK, ycK, 1.04), M_VAPEUR, sim)
    kscale(v, 1, 0, 'CONSTANT')
    f = 1298 + i * 5
    while f < 1350:
        kloc(v, f, (xcK, ycK, 1.04), 'LINEAR')
        kscale(v, f, 0.6, 'LINEAR')
        kloc(v, f + 33, (xcK + rnd.uniform(-0.08, 0.08), ycK, 1.50), 'CONSTANT')
        kscale(v, f + 33, 2.2, 'CONSTANT')
        f += 35
    kscale(v, f, 0, 'CONSTANT')

# manometre de la pompe a vide : l'aiguille part de zero quand on filtre
axe = D["F_pompe_axe_aiguille"]
e_aig = empty("SIM_rot_aiguille", axe.location.copy())
adopt(e_aig, [D["F_pompe_aiguille"]])
for f, a in ((1, -75), (600, -75), (625, 0), (770, 0), (790, -75), (1080, -75), (1105, 0),
             (1180, 0), (1200, -75)):
    krot(e_aig, f, (0, rad(a), 0), 'BEZIER')

# ================================================================== DEPART : on decale tout pour inserer l'entree
DELTA = 168                    # 7 s d'entree de la bauxite brute avant le broyage
apply_interpolations()
_reg.clear()


def decaler_tout(f_min, delta):
    for act in bpy.data.actions:
        fcs = []
        if hasattr(act, "layers"):
            for layer in act.layers:
                for strip in layer.strips:
                    for cb in strip.channelbags:
                        fcs.extend(cb.fcurves)
        else:
            fcs = list(act.fcurves)
        for fc in fcs:
            for kp in fc.keyframe_points:
                if kp.co.x >= f_min:
                    kp.co.x += delta
                    kp.handle_left.x += delta
                    kp.handle_right.x += delta
            fc.update()


decaler_tout(31, DELTA)


def T(f):
    return f if f < 31 else f + DELTA


sc.frame_end = T(1440)

# ================================================================== 1. ENTREE : bauxite brute + billes dans le fut (40-208)
rnd2 = random.Random(11)


def caillou(name, r, loc, m):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts:
        v.co *= rnd2.uniform(0.75, 1.2)
    bmesh.ops.scale(bm, vec=(1.0, rnd2.uniform(0.7, 1.0), rnd2.uniform(0.6, 0.9)), verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    sim.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (rnd2.uniform(0, 6.3), rnd2.uniform(0, 6.3), rnd2.uniform(0, 6.3))
    return ob


# seau en caoutchouc noir plein de bauxite en morceaux, devant le broyeur
BX, BY = X_A0 - 0.14, -0.50
lathe("SIM_seau_bauxite_brute", [(0, 0), (0.09, 0), (0.105, 0.17), (0.10, 0.17), (0.086, 0.004), (0, 0.004)],
      ns["M_NOIR"], sim, (BX, BY, 0))
cailloux = []
for i in range(18):
    a_ = rnd2.uniform(0, math.tau)
    rr = rnd2.uniform(0, 0.055)
    z = 0.035 + (i // 6) * 0.05 + rnd2.uniform(0, 0.02)
    cailloux.append(caillou("SIM_bauxite_brute", rnd2.uniform(0.022, 0.034),
                            (BX + rr * math.cos(a_), BY + rr * math.sin(a_), z), ns["M_BAUX"]))

# bac de billes d'acier
TX, TY = X_A0 + 0.30, -0.45
lathe("SIM_bac_billes", [(0, 0), (0.075, 0), (0.085, 0.06), (0.082, 0.06), (0.072, 0.003), (0, 0.003)],
      ns["M_TOLE"], sim, (TX, TY, 0))
billes = []
for i in range(10):
    a_ = rnd2.uniform(0, math.tau)
    rr = rnd2.uniform(0, 0.045)
    billes.append(ball("SIM_bille_acier", 0.016, (TX + rr * math.cos(a_), TY + rr * math.sin(a_),
                                                   0.02 + (i // 5) * 0.025), ns["M_INOX"], sim))

# couvercle : on le retire, on le pose au sol, puis on le remet
repos = Vector((X_A0 + 0.205, 0, ZD))
sol_c = Vector((X_A0 + 0.55, -0.15, 0.013))
haut_c = sol_c + Vector((0, 0, 0.08))
milieu = (X_A0 + 0.40, -0.25, 0.62)
for f, pos, ry in ((1, repos, 0), (58, repos, 0), (68, milieu, -45), (78, haut_c, -90), (82, sol_c, -90),
                   (172, sol_c, -90), (176, haut_c, -90), (186, milieu, -45), (196, repos, 0)):
    kloc(e_lid, f, pos)
    krot(e_lid, f, (0, rad(ry), 0), 'BEZIER')


def charger(objets, f_debut, pas, apex, cible_fn):
    for i, ob in enumerate(objets):
        f0 = f_debut + i * pas
        depart = ob.location.copy()
        kloc(ob, f0, depart)
        kloc(ob, f0 + 8, (apex[0], apex[1] + rnd2.uniform(-0.03, 0.03), apex[2]))
        kloc(ob, f0 + 16, cible_fn(), 'CONSTANT')
        r0 = ob.rotation_euler.copy()
        krot(ob, f0, r0)
        krot(ob, f0 + 16, (r0.x + 3, r0.y + 2, r0.z), 'CONSTANT')
        visible(ob, 1, 206)            # caches quand le fut est referme et tourne


charger(cailloux, 84, 3, (X_A0 + 0.33, -0.17, ZD + 0.20),
        lambda: (X_A0 + rnd2.uniform(-0.06, 0.12), rnd2.uniform(-0.07, 0.07), ZD - 0.10 + rnd2.uniform(0, 0.04)))
charger(billes, 140, 3, (X_A0 + 0.33, -0.14, ZD + 0.17),
        lambda: (X_A0 + rnd2.uniform(-0.10, 0.10), rnd2.uniform(-0.06, 0.06), ZD - 0.115))

# ================================================================== CAMERA
cam = sc.camera
cam.data.lens = 35
cible = empty("SIM_cible_camera", (0.05, 0, 0.85))
con = cam.constraints.new('TRACK_TO')
con.target = cible
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
plans = (
    ((1, 30),            (0.4, -7.7, 2.9),     (0.05, 0, 0.85)),      # vue d'ensemble
    ((62, 198),          (-1.45, -1.40, 0.95), (-2.28, -0.22, 0.38)), # entree de la bauxite
    ((T(62), T(200)),    (-1.75, -2.0, 1.25),  (-2.35, 0, 0.55)),     # broyeur
    ((T(250), T(590)),   (-0.55, -2.5, 1.75),  (-0.85, 0, 1.10)),     # R1
    ((T(620), T(770)),   (-0.35, -2.9, 1.60),  (-0.40, 0, 0.75)),     # R1 + filtre
    ((T(795), T(1200)),  (0.45, -2.9, 1.70),   (0.45, 0, 0.85)),      # filtre + R2
    ((T(1265), T(1388)), (2.62, -2.05, 1.30),  (2.40, -0.10, 0.74)),  # four
    ((T(1414), T(1440)), (2.40, -1.25, 0.98),  (2.37, -0.08, 0.66)),  # alumine
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
bande.visible_shadow = False             # le bandeau colle a la camera ne doit pas faire d'ombre
bande.location = (0, -0.236, -1.004)
legendes = (
    (1,       "De la bauxite à l'alumine  -  lot de 5 kg"),
    (40,      "1. ENTRÉE  -  5 kg de bauxite brute, en morceaux"),
    (138,     "On ajoute les billes d'acier, puis on referme le fût"),
    (T(40),   "2. BROYAGE  -  la bauxite est réduite en poudre (< 250 µm)"),
    (T(200),  "3. CHARGEMENT  -  eau + 3,5 kg de soude, puis 5 kg de poudre"),
    (T(290),  "4. ATTAQUE  -  100 °C, 2 h : l'alumine se dissout dans la soude"),
    (T(520),  "5. DÉCANTATION  -  les boues rouges tombent au fond"),
    (T(600),  "6. FILTRATION  -  vanne haute : la liqueur claire passe"),
    (T(700),  "7. Vanne basse : les boues rouges restent sur la toile"),
    (T(780),  "8. TRANSFERT  -  la liqueur d'aluminate va dans R2"),
    (T(860),  "9. PRÉCIPITATION  -  le CO2 fait apparaître l'hydrate blanc"),
    (T(1080), "10. FILTRATION  -  l'hydrate d'alumine reste sur la toile"),
    (T(1200), "11. L'hydrate lavé et séché part au four"),
    (T(1262), "12. CALCINATION  -  montée à 1050 °C : l'eau part en vapeur"),
    (T(1365), "13. REFROIDISSEMENT  -  porte fermée jusqu'à moins de 100 °C"),
    (T(1410), "ALUMINE  -  environ 1,9 kg de poudre blanche"),
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
for m in (m1, m2, M_FILTRAT, M_J_AMBRE, M_VAPEUR):
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
