# Animation du procede bauxite -> alumine (60 s a 24 images/s).
# Reconstruit la scene avec construire_usine.py puis ajoute les images cles.
# A lancer depuis un .blend enregistre dans le dossier du projet.

import bpy, math, os, random
from mathutils import Vector, Matrix

BASE = os.path.dirname(bpy.data.filepath)
build = os.path.join(BASE, "construire_usine.py")
ns = {"__name__": "build"}
exec(compile(open(build, encoding="utf-8").read(), build, "exec"), ns)
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
for o in named("A0_releveur"):
    bpy.data.objects.remove(o)
e_tamb = empty("SIM_rot_tambour", (X_A0, 0, ZD))
for a in (0, 120, 240):
    b = box("SIM_releveur", (0.38, 0.004, 0.02),
            (X_A0, 0.127 * math.cos(rad(a)), ZD + 0.127 * math.sin(rad(a))), ns["M_TOLE"], sim,
            rot=(rad(a + 90), 0, 0))
    adopt(e_tamb, [b])
spin(e_tamb, 40, 200, 0, 5)

e_poul = empty("SIM_rot_poulie", (X_A0 + 0.396, -0.10, 0.50))
mk = box("SIM_repere_poulie", (0.004, 0.014, 0.014), (X_A0 + 0.397, -0.10, 0.535), ns["M_BLANC"], sim)
adopt(e_poul, [mk])
spin(e_poul, 40, 200, 0, 14)

e_bil = empty("SIM_bascule_billes", (X_A0, 0, ZD))
adopt(e_bil, named("A0_bille_acier") + named("A0_bauxite"))
f = 40
krot(e_bil, f, (0, 0, 0))
while f < 196:
    krot(e_bil, f + 15, (rad(38), 0, 0))
    krot(e_bil, f + 21, (rad(4), 0, 0))
    f += 21
krot(e_bil, 200, (0, 0, 0))
for o in named("A0_bauxite"):          # les morceaux deviennent de la poudre
    kscale(o, 40, 1.6)
    kscale(o, 200, 0.35)

# ================================================================== 2. CHARGEMENT de R1 (200-290)
Z0 = 0.90
seau = lathe("SIM_seau", [(0, 0), (0.09, 0), (0.10, 0.16), (0.097, 0.16), (0.087, 0.003), (0, 0.003)],
             ns["M_COFFRET"], sim, (X_A0, -0.45, 0.75))
poudre = lathe("SIM_poudre_bauxite", [(0, 0), (0.087, 0), (0.094, 0.12), (0, 0.12)],
               ns["M_BAUX"], sim, (X_A0, -0.45, 0.753))
adopt(seau, [poudre])
kscale(seau, 1, 0, 'CONSTANT')
kscale(seau, 200, 0, 'LINEAR')
kscale(seau, 206, 1, 'CONSTANT')
kscale(seau, 296, 0, 'CONSTANT')
kloc(seau, 206, (X_A0, -0.45, 0.75))
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

# ================================================================== 10-11. FOUR (1200-1440)
kloc(hyd, 1200, (X_F, 0, 0.553))
kloc(hyd, 1230, (1.25, -0.95, 1.25))
kloc(hyd, 1258, (X_K, -0.155, 0.64))

alu = D["K_alumine"]
alu.data.transform(Matrix.Translation((0, 0, 0.015)))      # origine au fond de la couche
alu.location.z -= 0.015
kscale(alu, 1, 0, 'CONSTANT')
kscale(alu, 1260, 1, 'LINEAR')
kscale(alu, 1290, (1, 1, 1), 'LINEAR')
kscale(alu, 1370, (1, 1, 0.65), 'LINEAR')

e_porte = empty("SIM_rot_porte", (X_K - 0.28, -0.28, 0.73))
adopt(e_porte, named("K_porte") + named("K_poignee_porte"))
for f, a in ((1, 0), (1262, 0), (1290, 110), (1380, 110), (1402, 0)):
    krot(e_porte, f, (0, 0, rad(a)), 'BEZIER')

res = next(n for n in ns["M_RESIST"].node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]
for f, v in ((1, 0.3), (1285, 0.3), (1320, 10), (1385, 10), (1430, 1.5)):
    res.default_value = v
    res.keyframe_insert("default_value", frame=f)
    reg(ns["M_RESIST"].node_tree, None, f, 'LINEAR')
lum = bpy.data.lights.new("SIM_lueur_four", 'POINT')
lum.color = (1.0, 0.45, 0.1)
lum_o = bpy.data.objects.new("SIM_lueur_four", lum)
lum_o.location = (X_K, -0.15, 0.73)
sim.objects.link(lum_o)
for f, v in ((1, 0), (1285, 0), (1320, 40), (1385, 40), (1430, 4)):
    lum.energy = v
    lum.keyframe_insert("energy", frame=f)

M_VAPEUR = mat("SIM_vapeur", (1, 1, 1), 0, 0.9, alpha=0.5)
for i in range(7):
    v = ball("SIM_vapeur", 0.02, (X_K, -0.15, 1.06), M_VAPEUR, sim)
    kscale(v, 1, 0, 'CONSTANT')
    f = 1292 + i * 5
    while f < 1365:
        kloc(v, f, (X_K, -0.15, 1.06), 'LINEAR')
        kscale(v, f, 0.6, 'LINEAR')
        kloc(v, f + 33, (X_K + rnd.uniform(-0.08, 0.08), -0.15, 1.55), 'CONSTANT')
        kscale(v, f + 33, 2.2, 'CONSTANT')
        f += 35
    kscale(v, f, 0, 'CONSTANT')

# ================================================================== CAMERA
cam = sc.camera
cible = empty("SIM_cible_camera", (0.05, 0, 0.85))
con = cam.constraints.new('TRACK_TO')
con.target = cible
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
plans = (
    ((1, 30),      (0.4, -7.7, 2.9),     (0.05, 0, 0.85)),      # vue d'ensemble
    ((62, 200),    (-1.75, -2.0, 1.25),  (-2.35, 0, 0.55)),     # broyeur
    ((250, 590),   (-0.55, -2.5, 1.75),  (-0.85, 0, 1.10)),     # R1
    ((620, 770),   (-0.35, -2.9, 1.60),  (-0.40, 0, 0.75)),     # R1 + filtre
    ((795, 1200),  (0.45, -2.9, 1.70),   (0.45, 0, 0.85)),      # filtre + R2
    ((1265, 1390), (2.75, -2.5, 1.45),   (2.45, -0.1, 0.78)),   # four
    ((1412, 1440), (2.55, -1.55, 1.05),  (2.45, -0.15, 0.68)),  # alumine
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
bande.location = (0, -0.236, -1.004)
legendes = (
    (1,    "De la bauxite à l'alumine  -  lot de 5 kg"),
    (40,   "1. BROYAGE  -  la bauxite est réduite en poudre (< 250 µm)"),
    (200,  "2. CHARGEMENT  -  eau + 3,5 kg de soude, puis 5 kg de poudre"),
    (290,  "3. ATTAQUE  -  100 °C, 2 h : l'alumine se dissout dans la soude"),
    (520,  "4. DÉCANTATION  -  les boues rouges tombent au fond"),
    (600,  "5. FILTRATION  -  vanne haute : la liqueur claire passe"),
    (700,  "6. Vanne basse : les boues rouges restent sur la toile"),
    (780,  "7. TRANSFERT  -  la liqueur d'aluminate va dans R2"),
    (860,  "8. PRÉCIPITATION  -  le CO2 fait apparaître l'hydrate blanc"),
    (1080, "9. FILTRATION  -  l'hydrate d'alumine reste sur la toile"),
    (1200, "10. L'hydrate lavé et séché part au four"),
    (1262, "11. CALCINATION  -  1050 °C : l'eau part en vapeur"),
    (1402, "ALUMINE  -  environ 1,9 kg de poudre blanche"),
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
    ob.location = (0, -0.245, -1.0)
    f1 = legendes[i + 1][0] if i + 1 < len(legendes) else None
    visible(ob, f0, f1)

apply_interpolations()
sc.frame_set(1)
print("Animation prete :", sc.frame_end, "images,", round(sc.frame_end / sc.render.fps), "s")
