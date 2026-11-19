# Materiaux realistes pour la mini-usine bauxite -> alumine.
# A lancer apres construire_usine.py, dans la scene ouverte.
# Remplace les couleurs "dessin" par des materiaux reels (inox brosse, acier brut,
# fonte, brique refractaire, laine de roche, beton...), ajoute des chanfreins
# pour accrocher la lumiere, un ciel physique, un sol en beton et un mur.

import bpy, bmesh, math
from mathutils import Vector

sc = bpy.context.scene


# ------------------------------------------------------------------ outils noeuds
def rgba(v):
    if isinstance(v, (int, float)):
        return (v, v, v, 1)
    return (*v, 1) if len(v) == 3 else tuple(v)


def sock(coll, key):
    for s in coll:
        if s.identifier == key:
            return s
    for s in coll:
        if s.name == key and getattr(s, "enabled", True):
            return s
    return coll[key]


class NB:
    """Construit un materiau Principled a partir de zero."""

    def __init__(self, m):
        try:
            m.use_nodes = True
        except Exception:
            pass
        self.m = m
        self.nt = m.node_tree
        self.nt.nodes.clear()
        out = self.nt.nodes.new("ShaderNodeOutputMaterial")
        self.bsdf = self.nt.nodes.new("ShaderNodeBsdfPrincipled")
        self.nt.links.new(self.bsdf.outputs[0], sock(out.inputs, "Surface"))
        self.coord = None
        try:
            m.surface_render_method = 'DITHERED'
        except Exception:
            pass

    def new(self, t, **props):
        n = self.nt.nodes.new(t)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def set(self, name, v):
        s = sock(self.bsdf.inputs, name)
        s.default_value = rgba(v) if s.type == 'RGBA' else v

    def to(self, name, src):
        if isinstance(src, bpy.types.NodeSocket):
            self.link(src, sock(self.bsdf.inputs, name))
        else:
            self.set(name, src)

    def obj(self):
        if self.coord is None:
            self.coord = self.new("ShaderNodeTexCoord")
        return self.coord.outputs["Object"]

    def noise(self, scale, detail=4.0, rough=0.5, stretch=None):
        n = self.new("ShaderNodeTexNoise")
        sock(n.inputs, "Scale").default_value = scale
        sock(n.inputs, "Detail").default_value = detail
        sock(n.inputs, "Roughness").default_value = rough
        v = self.obj()
        if stretch:
            mp = self.new("ShaderNodeMapping")
            sock(mp.inputs, "Scale").default_value = stretch
            self.link(v, sock(mp.inputs, "Vector"))
            v = mp.outputs["Vector"]
        self.link(v, sock(n.inputs, "Vector"))
        return n.outputs["Fac"]

    def voronoi(self, scale):
        n = self.new("ShaderNodeTexVoronoi")
        sock(n.inputs, "Scale").default_value = scale
        self.link(self.obj(), sock(n.inputs, "Vector"))
        return sock(n.outputs, "Distance")

    def ramp(self, fac, stops):
        r = self.new("ShaderNodeValToRGB")
        els = r.color_ramp.elements
        els[0].position = stops[0][0]
        els[1].position = stops[-1][0]
        for p, _ in stops[1:-1]:
            els.new(p)
        for e, (_, v) in zip(sorted(els, key=lambda e: e.position), stops):
            e.color = rgba(v)
        self.link(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    def mix(self, fac, a, b):
        n = self.new("ShaderNodeMix", data_type='RGBA')
        self.link(fac, sock(n.inputs, "Factor_Float"))
        for key, val in (("A_Color", a), ("B_Color", b)):
            s = sock(n.inputs, key)
            if isinstance(val, bpy.types.NodeSocket):
                self.link(val, s)
            else:
                s.default_value = rgba(val)
        return sock(n.outputs, "Result_Color")

    def bump(self, h, strength, dist=0.002):
        b = self.new("ShaderNodeBump")
        sock(b.inputs, "Strength").default_value = strength
        try:
            sock(b.inputs, "Distance").default_value = dist
        except Exception:
            pass
        self.link(h, sock(b.inputs, "Height"))
        self.link(b.outputs["Normal"], sock(self.bsdf.inputs, "Normal"))


# ------------------------------------------------------------------ recettes
def inox_brosse(m):                       # cuves, vannes, arbres, tubes : inox 304 brosse
    b = NB(m)
    traits = b.noise(2.0, 6, 0.6, stretch=(6, 6, 900))
    traces = b.noise(2.5, 3, 0.5)
    b.to("Base Color", b.ramp(traces, [(0.3, (0.50, 0.50, 0.49)), (0.7, (0.62, 0.62, 0.61))]))
    b.to("Roughness", b.ramp(traits, [(0.3, 0.17), (0.7, 0.33)]))
    b.set("Metallic", 1.0)
    b.set("Anisotropic", 0.45)
    b.bump(traits, 0.03, 0.0005)


def inox_tole(m):                         # habillages : tole inox finition 2B (mate)
    b = NB(m)
    taches = b.noise(3.0, 4, 0.55)
    b.to("Base Color", b.ramp(taches, [(0.3, (0.48, 0.48, 0.47)), (0.7, (0.56, 0.56, 0.55))]))
    b.to("Roughness", b.ramp(taches, [(0.25, 0.30), (0.75, 0.45)]))
    b.set("Metallic", 1.0)


def acier_brut(m):                        # corniere acier laminee a chaud (calamine), un peu de rouille
    b = NB(m)
    calamine = b.noise(9.0, 8, 0.6)
    base = b.ramp(calamine, [(0.35, (0.040, 0.043, 0.047)), (0.65, (0.105, 0.105, 0.11))])
    rouille = b.ramp(b.noise(3.0, 10, 0.65), [(0.66, 0.0), (0.73, 1.0)])
    b.to("Base Color", b.mix(rouille, base, (0.17, 0.055, 0.02)))
    b.to("Roughness", b.mix(rouille, b.ramp(calamine, [(0.3, 0.38), (0.7, 0.62)]), 0.92))
    b.to("Metallic", b.mix(rouille, 0.8, 0.0))
    b.bump(b.noise(60.0, 6, 0.6), 0.08)


def peinture(rgb, rough=0.38, coat=0.3):  # peinture industrielle (moteurs, bouteille)
    def f(m):
        b = NB(m)
        b.set("Base Color", rgb)
        b.to("Roughness", b.ramp(b.noise(4.0, 3), [(0.3, rough - 0.05), (0.7, rough + 0.08)]))
        b.set("Coat Weight", coat)
        b.set("Coat Roughness", 0.25)
        b.bump(b.noise(250.0, 2), 0.02)    # peau d'orange
    return f


def plastique(rgb, rough=0.45):           # coffrets ABS, bac PE
    def f(m):
        b = NB(m)
        b.set("Base Color", rgb)
        b.set("Roughness", rough)
        b.bump(b.noise(400.0, 2), 0.03)
    return f


def caoutchouc(m):
    b = NB(m)
    b.set("Base Color", (0.018, 0.018, 0.018))
    b.to("Roughness", b.ramp(b.noise(5.0), [(0.3, 0.55), (0.7, 0.7)]))
    b.bump(b.noise(300.0, 2), 0.05)


def vinyle_rouge(m):                      # poignees de vanne gainees
    b = NB(m)
    b.set("Base Color", (0.50, 0.018, 0.012))
    b.set("Roughness", 0.35)
    b.set("Coat Weight", 0.4)


def fonte(m):                             # plaque chauffante en fonte
    b = NB(m)
    g = b.noise(40.0, 8, 0.7)
    b.to("Base Color", b.ramp(g, [(0.3, (0.025, 0.025, 0.026)), (0.7, (0.06, 0.06, 0.06))]))
    b.to("Roughness", b.ramp(g, [(0.3, 0.45), (0.7, 0.7)]))
    b.set("Metallic", 0.6)
    b.bump(g, 0.15)


def afficheur(m):                         # afficheur 7 segments rouge du regulateur
    b = NB(m)
    b.set("Base Color", (0.01, 0.0, 0.0))
    b.set("Roughness", 0.1)
    b.set("Emission Color", (1.0, 0.08, 0.03))
    b.set("Emission Strength", 4.0)


def brique_isolante(m):                   # brique refractaire isolante (beige, poreuse)
    b = NB(m)
    pores = b.voronoi(180.0)
    var = b.noise(6.0, 6, 0.6)
    b.to("Base Color", b.ramp(var, [(0.3, (0.60, 0.50, 0.34)), (0.7, (0.78, 0.68, 0.50))]))
    b.set("Roughness", 0.95)
    b.bump(pores, 0.35)


def resistance(m):                        # fil Kanthal froid (gris oxyde)
    b = NB(m)
    b.set("Base Color", (0.30, 0.29, 0.27))
    b.set("Metallic", 1.0)
    b.set("Roughness", 0.55)


def laine_de_roche(m):                    # jaune-olive fibreux
    b = NB(m)
    fibres = b.noise(120.0, 12, 0.75, stretch=(1, 1, 0.15))
    var = b.noise(5.0, 4, 0.6)
    b.to("Base Color", b.ramp(var, [(0.3, (0.32, 0.22, 0.065)), (0.7, (0.52, 0.38, 0.12))]))
    b.set("Roughness", 1.0)
    b.bump(fibres, 0.5)


def fibre_ceramique(m):                   # isolation de chambre de four : blanc casse, fibreux
    b = NB(m)
    var = b.noise(8.0, 5, 0.6)
    b.to("Base Color", b.ramp(var, [(0.3, (0.70, 0.68, 0.62)), (0.7, (0.82, 0.80, 0.74))]))
    b.set("Roughness", 1.0)
    b.bump(b.noise(300.0, 10, 0.7), 0.2)


def afficheur_vert(m):
    b = NB(m)
    b.set("Base Color", (0.0, 0.01, 0.0))
    b.set("Roughness", 0.1)
    b.set("Emission Color", (0.15, 1.0, 0.2))
    b.set("Emission Strength", 3.0)


def poudre_blanche(m):                    # alumine / toile polypropylene
    b = NB(m)
    b.set("Base Color", (0.83, 0.83, 0.81))
    b.set("Roughness", 0.9)
    b.bump(b.noise(500.0, 4), 0.12)


def boue_rouge(m):                        # boue rouge humide
    b = NB(m)
    v = b.noise(25.0, 6, 0.6)
    b.to("Base Color", b.ramp(v, [(0.3, (0.14, 0.03, 0.012)), (0.7, (0.24, 0.06, 0.024))]))
    b.to("Roughness", b.ramp(v, [(0.3, 0.2), (0.7, 0.45)]))
    b.bump(v, 0.25)


def bauxite(m):                           # bauxite rouge-brun, seche
    b = NB(m)
    v = b.noise(30.0, 8, 0.65)
    b.to("Base Color", b.ramp(v, [(0.3, (0.26, 0.085, 0.032)), (0.7, (0.42, 0.16, 0.06))]))
    b.set("Roughness", 0.95)
    b.bump(v, 0.6)


def beton(m):                             # dalle beton lissee
    b = NB(m)
    v = b.noise(1.5, 8, 0.6)
    fin = b.noise(80.0, 6, 0.6)
    b.to("Base Color", b.ramp(v, [(0.3, (0.26, 0.255, 0.24)), (0.7, (0.38, 0.37, 0.35))]))
    b.to("Roughness", b.ramp(v, [(0.3, 0.6), (0.7, 0.85)]))
    b.bump(fin, 0.12)


def enduit(m):                            # mur en parpaings enduit
    b = NB(m)
    v = b.noise(0.8, 6, 0.55)
    b.to("Base Color", b.ramp(v, [(0.2, (0.36, 0.34, 0.30)), (0.8, (0.42, 0.40, 0.355))]))
    b.set("Roughness", 0.92)
    b.bump(b.noise(60.0, 8, 0.7), 0.3)


def verre(m):                             # piege a liquide, debitmetre
    b = NB(m)
    b.set("Base Color", (0.93, 0.97, 0.97))
    b.set("Roughness", 0.02)
    b.set("IOR", 1.49)
    b.set("Transmission Weight", 1.0)
    for p in ("use_raytrace_refraction", "use_screen_refraction"):
        if hasattr(m, p):
            setattr(m, p, True)


def pulpe_rouge(m):                       # bauxite + soude en suspension : opaque, brillant
    b = NB(m)
    b.set("Base Color", (0.18, 0.045, 0.02))
    b.set("Roughness", 0.06)


def suspension_blanche(m):                # hydrate d'alumine en suspension : laiteux
    b = NB(m)
    b.set("Base Color", (0.80, 0.81, 0.79))
    b.set("Roughness", 0.05)
    b.set("Subsurface Weight", 1.0)
    b.set("Subsurface Scale", 0.01)


RECETTES = {
    "Inox": inox_brosse,
    "Tole": inox_tole,
    "Chassis acier peint": acier_brut,
    "Laine de roche": laine_de_roche,
    "Caoutchouc noir": caoutchouc,
    "Poignee rouge": vinyle_rouge,
    "Moteur": peinture((0.11, 0.15, 0.21)),
    "Plaque chauffante": fonte,
    "Coffret": plastique((0.60, 0.60, 0.58)),
    "Afficheur": afficheur,
    "Brique refractaire": brique_isolante,
    "Resistance Kanthal": resistance,
    "Alumine / toile PP": poudre_blanche,
    "Boue rouge": boue_rouge,
    "Bauxite": bauxite,
    "Bac de retention": plastique((0.010, 0.055, 0.21), 0.55),
    "Bouteille CO2": peinture((0.19, 0.20, 0.21), 0.32, 0.6),
    "Sol": beton,
    "Peinture four": peinture((0.56, 0.57, 0.55), 0.42, 0.1),     # tole peinte epoxy, gris clair RAL 7035
    "Panneau commande": peinture((0.035, 0.04, 0.045), 0.45, 0.2),  # anthracite
    "Fibre ceramique": fibre_ceramique,
    "Peinture fut": peinture((0.008, 0.035, 0.11), 0.4, 0.3),        # fut acier peint bleu
    "Peinture jaune": peinture((0.85, 0.40, 0.0), 0.4, 0.2),         # carter de securite, potence
    "Peinture verte securite": peinture((0.02, 0.30, 0.09), 0.4, 0.3),  # douche / rince-oeil
    "Combinaison de travail": plastique((0.035, 0.08, 0.20), 0.9),
    "Gant nitrile": plastique((0.04, 0.25, 0.10), 0.45),
    "Mannequin": plastique((0.50, 0.50, 0.48), 0.6),
    "Afficheur vert": afficheur_vert,
    "Piege transparent": verre,
    "R1_Attaque_mat_liquide": pulpe_rouge,
    "R2_Precipitation_mat_liquide": suspension_blanche,
    "Suspension blanche": suspension_blanche,
}
NOMS = {"Chassis acier peint": "Acier corniere brut", "Moteur": "Peinture moteur",
        "Tole": "Tole inox 2B", "Inox": "Inox 304 brosse"}

faits = []
for m in list(bpy.data.materials):
    base = m.name.split(".")[0]
    f = RECETTES.get(base)
    if not f:
        continue
    nt_anim = m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action
    if nt_anim:                           # materiau anime (fichier d'animation) : on n'y touche pas
        continue
    f(m)
    if base in NOMS:
        m.name = NOMS[base]
    faits.append(m.name)


# ------------------------------------------------------------------ chanfreins
SANS_CHANFREIN = ("liquide", "bulle", "vapeur", "bille", "bauxite", "Sol", "Mur", "SIM_", "etiquette", "chevalet",
                  "chaine", "panneau", "_texte", "Operateur")
n_bev = 0
for ob in sc.objects:
    if ob.type != 'MESH' or "Chanfrein" in ob.modifiers:
        continue
    if any(k in ob.name for k in SANS_CHANFREIN):
        continue
    me = ob.data
    if me.polygons and not any(p.use_smooth for p in me.polygons):
        for p in me.polygons:
            p.use_smooth = True
    md = ob.modifiers.new("Chanfrein", 'BEVEL')
    md.width = 0.0015
    md.segments = 2
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(30)
    md.use_clamp_overlap = True
    try:
        md.harden_normals = True
    except Exception:
        pass
    n_bev += 1


# ------------------------------------------------------------------ atelier : sol, mur, annotations
sol = bpy.data.objects.get("Sol")
if sol:
    sol.scale = (7.0, 14.0, 1.0)         # dalle de ~50 x 50 m : pas de bord visible

if "Mur_atelier" not in bpy.data.objects:
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(50.0, 0.2, 4.0), verts=bm.verts)
    me = bpy.data.meshes.new("Mur_atelier")
    bm.to_mesh(me)
    bm.free()
    m_mur = bpy.data.materials.new("Mur enduit")
    enduit(m_mur)
    me.materials.append(m_mur)
    mur = bpy.data.objects.new("Mur_atelier", me)
    mur.location = (0.1, 2.6, 2.0)
    (sol.users_collection[0] if sol else sc.collection).objects.link(mur)

for ob in sc.objects:                     # etiquettes et reperes : caches pour une vue "photo"
    if ob.name.startswith(("Txt_", "Regle_1m", "Repere_personne")):
        ob.hide_viewport = True
        ob.hide_render = True


# ------------------------------------------------------------------ lumiere : ciel physique + soleil
world = sc.world or bpy.data.worlds.new("Monde")
sc.world = world
try:
    world.use_nodes = True
except Exception:
    pass
wn = world.node_tree
wn.nodes.clear()
w_out = wn.nodes.new("ShaderNodeOutputWorld")
w_bg = wn.nodes.new("ShaderNodeBackground")
w_sky = wn.nodes.new("ShaderNodeTexSky")
types = [i.identifier for i in w_sky.bl_rna.properties["sky_type"].enum_items]
w_sky.sky_type = next((t for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA") if t in types), types[0])
for k, v in (("sun_disc", False), ("sun_elevation", math.radians(40)), ("sun_rotation", math.radians(205)),
             ("air_density", 1.0), ("aerosol_density", 1.5)):
    try:
        setattr(w_sky, k, v)
    except Exception:
        pass
wn.links.new(w_sky.outputs[0], sock(w_bg.inputs, "Color"))
sock(w_bg.inputs, "Strength").default_value = 0.15
wn.links.new(w_bg.outputs[0], sock(w_out.inputs, "Surface"))

sun = bpy.data.objects.get("Soleil")
if sun:
    sun.data.energy = 4.5
    sun.data.angle = math.radians(1.5)
    sun.data.color = (1.0, 0.96, 0.90)
app = bpy.data.objects.get("Appoint")
if app:                                   # lampe d'appoint : aplatit l'image, on l'eteint
    app.hide_render = True
    app.hide_viewport = True

# ------------------------------------------------------------------ rendu
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        sc.render.engine = eng
        break
    except TypeError:
        pass
ee = sc.eevee
for k, v in (("use_raytracing", True), ("use_shadows", True), ("use_fast_gi", True),
             ("taa_render_samples", 64), ("taa_samples", 16), ("shadow_ray_count", 2)):
    try:
        setattr(ee, k, v)
    except Exception:
        pass
vs = sc.view_settings
for cand in ("AgX", "Filmic"):            # liste dynamique : on essaie directement
    try:
        vs.view_transform = cand
        break
    except TypeError:
        pass
for lk in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try:
        vs.look = lk
        break
    except TypeError:
        pass
vs.exposure = -0.6

# camera "photo" fixe
cam = bpy.data.objects.get("Camera_Photo")
if not cam:
    cam = bpy.data.objects.new("Camera_Photo", bpy.data.cameras.new("Camera_Photo"))
    sc.collection.objects.link(cam)
cam.data.lens = 28
cam.location = (0.25, -5.3, 1.75)
cam.rotation_euler = (Vector((0.05, 0.0, 0.75)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

print("materiaux refaits :", len(faits), "| chanfreins :", n_bev, "| ciel :", w_sky.sky_type,
      "| moteur :", sc.render.engine, "| couleurs :", vs.view_transform)
