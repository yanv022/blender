# Mini-usine bauxite -> alumine : construction de la scene Blender
# Unites : metres. A lancer dans un fichier Blender vide (le script efface la scene).
# Cotes issues de plan-usine-bauxite-alumine.md

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

scene = bpy.context.scene

# ------------------------------------------------------------------ nettoyage
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
               bpy.data.lights, bpy.data.cameras):
    for b in list(blocks):
        if b.users == 0:
            blocks.remove(b)

# ------------------------------------------------------------------ materiaux
def mat(name, rgb, metal=0.0, rough=0.5, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (*rgb, alpha)
    return m

M_INOX   = mat("Inox", (0.72, 0.74, 0.77), 0.7, 0.35)
M_TOLE   = mat("Tole", (0.45, 0.47, 0.50), 0.5, 0.5)
M_CHASSIS= mat("Chassis acier peint", (0.08, 0.17, 0.30), 0.2, 0.5)
M_ISOL   = mat("Laine de roche", (0.80, 0.66, 0.25), 0.0, 0.95)
M_NOIR   = mat("Caoutchouc noir", (0.03, 0.03, 0.03), 0.0, 0.7)
M_ROUGE  = mat("Poignee rouge", (0.75, 0.05, 0.04), 0.0, 0.4)
M_MOTEUR = mat("Moteur", (0.05, 0.30, 0.22), 0.3, 0.5)
M_PLAQUE = mat("Plaque chauffante", (0.12, 0.12, 0.13), 0.6, 0.6)
M_COFFRET= mat("Coffret", (0.82, 0.82, 0.80), 0.1, 0.5)
M_ECRAN  = mat("Afficheur", (0.1, 1.0, 0.3), 0.0, 0.4, emit=3.0)
M_BRIQUE = mat("Brique refractaire", (0.90, 0.84, 0.70), 0.0, 0.95)
M_RESIST = mat("Resistance Kanthal", (1.0, 0.30, 0.04), 0.0, 0.5, emit=4.0)
M_BLANC  = mat("Alumine / toile PP", (0.95, 0.95, 0.93), 0.0, 0.8)
M_BOUE   = mat("Boue rouge", (0.45, 0.10, 0.05), 0.0, 0.9)
M_BAUX   = mat("Bauxite", (0.55, 0.22, 0.10), 0.0, 0.9)
M_BAC    = mat("Bac de retention", (0.05, 0.25, 0.55), 0.0, 0.5)
M_CO2    = mat("Bouteille CO2", (0.30, 0.32, 0.35), 0.6, 0.4)
M_SOL    = mat("Sol", (0.50, 0.50, 0.48), 0.0, 0.9)
M_TEXTE  = mat("Texte", (0.02, 0.02, 0.02), 0.0, 0.8)
M_LIQ    = mat("Suspension blanche", (0.92, 0.93, 0.95), 0.0, 0.3, alpha=0.45)
M_VERRE  = mat("Piege transparent", (0.80, 0.90, 0.95), 0.0, 0.1, alpha=0.35)
M_REPERE = mat("Repere", (0.60, 0.60, 0.62), 0.0, 0.8, alpha=0.5)
M_FOUR   = mat("Peinture four", (0.56, 0.57, 0.55), 0.0, 0.42)
M_PANNEAU= mat("Panneau commande", (0.035, 0.04, 0.045), 0.0, 0.45)
M_FIBRE  = mat("Fibre ceramique", (0.80, 0.77, 0.70), 0.0, 0.95)
M_ECRAN_V= mat("Afficheur vert", (0.1, 1.0, 0.2), 0.0, 0.4, emit=3.0)
M_FUT    = mat("Peinture fut", (0.01, 0.04, 0.12), 0.0, 0.4)
M_JAUNE  = mat("Peinture jaune", (0.85, 0.40, 0.0), 0.0, 0.4)

# ------------------------------------------------------------------ outils
def coll(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

def finish(name, bm, m, c, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35):
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    c.objects.link(ob)
    return ob

def rod(name, p1, p2, r, m, c, seg=24):
    """Cylindre plein entre deux points."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r, depth=d.length)
    ob = finish(name, bm, m, c)
    ob.location = (p1 + p2) / 2
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return ob

def box(name, size, center, m, c, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    ob = finish(name, bm, m, c, smooth=False)
    ob.location = center
    ob.rotation_euler = rot
    return ob

def ball(name, r, center, m, c):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=r)
    ob = finish(name, bm, m, c)
    ob.location = center
    return ob

def lathe(name, prof, m, c, loc=(0, 0, 0), start=0, sweep=360, steps=64, rot=(0, 0, 0)):
    """Solide de revolution autour de Z. prof = [(rayon, z), ...] polygone ferme.
    sweep < 360 donne une vue en coupe (secteur retire)."""
    bm = bmesh.new()
    a0 = math.radians(start)
    vs = [bm.verts.new((r * math.cos(a0), r * math.sin(a0), z)) for r, z in prof]
    start_co = [v.co.copy() for v in vs]
    n = len(vs)
    if sweep < 360:
        f = bm.faces.new(vs)
        geom = [f] + list(f.edges) + list(f.verts)
    else:
        es = [bm.edges.new((vs[i], vs[(i + 1) % n])) for i in range(n)]
        geom = vs + es
    bmesh.ops.spin(bm, geom=geom, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=math.radians(sweep), steps=max(3, int(steps * sweep / 360)),
                   use_merge=(sweep >= 360), use_duplicate=False)
    if sweep < 360:
        # refermer la face de depart (l'extrusion la laisse ouverte)
        bm.verts.ensure_lookup_table()
        cap = []
        for co in start_co:
            cap.append(min(bm.verts, key=lambda v: (v.co - co).length_squared))
        try:
            bm.faces.new(cap)
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    ob = finish(name, bm, m, c)
    ob.location = loc
    ob.rotation_euler = rot
    return ob

def hose(name, pts, r, m, c):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.materials.append(m)
    ob = bpy.data.objects.new(name, cu)
    c.objects.link(ob)
    return ob

def label(name, txt, loc, size, c):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = txt
    cu.size = size
    cu.align_x = 'CENTER'
    cu.extrude = 0.002
    cu.materials.append(M_TEXTE)
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = (math.pi / 2, 0, 0)
    c.objects.link(ob)
    return ob

def frame(prefix, X, hx, hy, h, c, y0=0.0, rails=(None,)):
    """4 pieds en corniere 40x40 + ceintures horizontales aux hauteurs 'rails'."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"{prefix}_pied", (0.04, 0.04, h), (X + sx * hx, y0 + sy * hy, h / 2), M_CHASSIS, c)
    for z in rails:
        for sy in (-1, 1):
            box(f"{prefix}_traverse", (2 * hx, 0.04, 0.04), (X, y0 + sy * hy, z), M_CHASSIS, c)
        for sx in (-1, 1):
            box(f"{prefix}_traverse", (0.04, 2 * hy, 0.04), (X + sx * hx, y0, z), M_CHASSIS, c)

CUT = (-45, 270)     # vue en coupe : quart avant retire (centre sur -Y)
FULL = (0, 360)

# ================================================================== CUVE R
def reactor(tag, X, side, cut, co2, liq_rgb=(0.92, 0.93, 0.95), liq_alpha=0.45):
    """Cuve agitee chauffee 50 L. side=+1 : vannes vers +X ; side=-1 : vers -X."""
    c = coll(tag)
    Z0, R, H = 0.90, 0.20, 0.40           # fond de cuve, rayon, hauteur
    st, sw = CUT if cut else FULL

    def pol(r, th, z):
        a = math.radians(th)
        return (X + side * r * math.cos(a), r * math.sin(a), z)

    def angw(th):
        return math.radians(th if side > 0 else 180 - th)

    # chassis + portique
    frame(tag + "_chassis", X, 0.28, 0.28, 0.84, c, rails=(0.30, 0.82))
    for sx in (-1, 1):
        box(tag + "_montant_portique", (0.04, 0.04, 0.60), (X + sx * 0.28, 0.28, 1.14), M_CHASSIS, c)
    box(tag + "_poutre_portique", (0.60, 0.04, 0.04), (X, 0.28, 1.42), M_CHASSIS, c)
    box(tag + "_platine_moteur", (0.14, 0.40, 0.008), (X, 0.10, 1.444), M_CHASSIS, c)
    box(tag + "_tablette", (0.64, 0.64, 0.006), (X, 0, 0.843), M_TOLE, c)

    # plaque chauffante 3 kW
    box(tag + "_plaque_3kW", (0.42, 0.42, 0.05), (X, 0, 0.871), M_PLAQUE, c)
    rod(tag + "_disque_chauffant", (X, 0, 0.894), (X, 0, 0.90), 0.17, M_NOIR, c, 48)

    # cuve, isolation, couvercle
    t = 0.003
    lathe(tag + "_cuve_inox_50L",
          [(0, Z0), (R, Z0), (R, Z0 + H), (R - t, Z0 + H), (R - t, Z0 + 0.006), (0, Z0 + 0.006)],
          M_INOX, c, (X, 0, 0), st, sw)
    lathe(tag + "_isolation_50mm",
          [(R + 0.002, Z0 + 0.11), (R + 0.050, Z0 + 0.11), (R + 0.050, Z0 + 0.39), (R + 0.002, Z0 + 0.39)],
          M_ISOL, c, (X, 0, 0), st, sw)
    lathe(tag + "_habillage_tole",
          [(R + 0.050, Z0 + 0.105), (R + 0.052, Z0 + 0.105), (R + 0.052, Z0 + 0.395), (R + 0.050, Z0 + 0.395)],
          M_TOLE, c, (X, 0, 0), st, sw)
    lathe(tag + "_couvercle",
          [(0.011, Z0 + H), (R + 0.006, Z0 + H), (R + 0.006, Z0 + H + 0.003), (0.011, Z0 + H + 0.003)],
          M_INOX, c, (X, 0, 0), st, sw)

    # agitateur
    box(tag + "_reducteur", (0.10, 0.10, 0.08), (X, 0, 1.488), M_MOTEUR, c)
    rod(tag + "_moteur_200W", (X, 0, 1.528), (X, 0, 1.70), 0.055, M_MOTEUR, c, 32)
    rod(tag + "_capot_ventilateur", (X, 0, 1.70), (X, 0, 1.73), 0.058, M_NOIR, c, 32)
    rod(tag + "_accouplement", (X, 0, 1.38), (X, 0, 1.43), 0.016, M_NOIR, c)
    rod(tag + "_arbre_D14", (X, 0, Z0 + 0.06), (X, 0, 1.448), 0.007, M_INOX, c)
    rod(tag + "_moyeu_turbine", (X, 0, Z0 + 0.05), (X, 0, Z0 + 0.08), 0.016, M_INOX, c)
    for k in range(4):
        th = 45 + 90 * k
        box(tag + "_pale_45deg", (0.05, 0.003, 0.032), pol(0.04, th, Z0 + 0.065), M_INOX, c,
            rot=(math.radians(45), 0, angw(th)))
    for th in (90, 200, 340):
        box(tag + "_chicane", (0.035, 0.004, 0.30), pol(R - 0.026, th, Z0 + 0.19), M_INOX, c,
            rot=(0, 0, angw(th)))

    # piquages du couvercle
    zc = Z0 + H + 0.003
    rod(tag + "_doigt_de_gant_sonde", pol(0.14, 180, Z0 + 0.08), pol(0.14, 180, zc + 0.06), 0.005, M_INOX, c)
    box(tag + "_tete_sonde", (0.04, 0.04, 0.04), pol(0.14, 180, zc + 0.08), M_COFFRET, c)
    rod(tag + "_trappe_chargement_D90", pol(0.125, 345, zc), pol(0.125, 345, zc + 0.03), 0.045, M_INOX, c, 32)
    ball(tag + "_bouton_trappe", 0.012, pol(0.125, 345, zc + 0.04), M_NOIR, c)
    v0, v1 = pol(0.13, 150, Z0 + H), pol(0.13, 150, 1.62)
    rod(tag + "_event_D25", v0, v1, 0.0125, M_INOX, c)
    ball(tag + "_coude_event", 0.0125, v1, M_INOX, c)
    rod(tag + "_event_vers_exterieur", v1, (v1[0], v1[1] + 0.50, 1.62), 0.0125, M_INOX, c)

    # vannes DN25 : basse (boues) et haute (liquide clair) + goulottes vers le filtre
    for nom, th, dz in (("basse", -15, 0.022), ("haute", 15, 0.075)):
        z = Z0 + dz
        rod(f"{tag}_piquage_{nom}", pol(R - 0.001, th, z), pol(0.30, th, z), 0.017, M_INOX, c)
        rod(f"{tag}_vanne_{nom}_DN25", pol(0.30, th, z), pol(0.37, th, z), 0.026, M_INOX, c)
        ball(f"{tag}_boisseau_{nom}", 0.033, pol(0.335, th, z), M_INOX, c)
        rod(f"{tag}_tige_{nom}", pol(0.335, th, z + 0.03), pol(0.335, th, z + 0.05), 0.006, M_INOX, c)
        box(f"{tag}_poignee_{nom}", (0.11, 0.016, 0.006), pol(0.37, th, z + 0.052), M_ROUGE, c,
            rot=(0, 0, angw(th)))
        p_out = pol(0.41, th, z)
        rod(f"{tag}_sortie_{nom}", pol(0.37, th, z), p_out, 0.017, M_INOX, c)
        ball(f"{tag}_coude_{nom}", 0.017, p_out, M_INOX, c)
        rod(f"{tag}_goulotte_{nom}", p_out, (X + side * 0.74, 0.03 if th > 0 else -0.03, 0.83),
            0.017, M_INOX, c)

    # coffret de regulation PID
    bx = X - side * 0.28
    box(tag + "_coffret_PID", (0.20, 0.10, 0.26), (bx, 0.21, 1.10), M_COFFRET, c)
    box(tag + "_afficheur", (0.08, 0.004, 0.035), (bx, 0.158, 1.17), M_ECRAN, c)

    if cut:
        # origine de l'objet au fond de la cuve : l'echelle Z regle le niveau
        lathe(tag + "_liquide",
              [(0, 0), (R - t, 0), (R - t, 0.229), (0, 0.229)],
              mat(tag + "_mat_liquide", liq_rgb, 0.0, 0.3, alpha=liq_alpha),
              c, (X, 0, Z0 + 0.006), st, sw)

    if co2:
        # tube plongeur + anneau perce sous la turbine
        zt = Z0 + 0.03
        rod(tag + "_tube_plongeur_CO2", pol(0.12, 215, zc + 0.10), pol(0.12, 215, zt), 0.005, M_INOX, c)
        rod(tag + "_clapet_anti_retour", pol(0.12, 215, zc + 0.10), pol(0.12, 215, zc + 0.15), 0.012, M_INOX, c)
        rod(tag + "_raccord_anneau", pol(0.12, 215, zt), pol(0.07, 215, zt), 0.005, M_INOX, c)
        circ = [(0.07 + 0.005 * math.cos(a), zt + 0.005 * math.sin(a))
                for a in [i * math.tau / 10 for i in range(10)]]
        lathe(tag + "_anneau_diffuseur", circ, M_INOX, c, (X, 0, 0))
        # bouteille sur balance
        bxc, byc = X - side * 0.62, -0.05
        box(tag + "_balance", (0.30, 0.30, 0.05), (bxc, byc, 0.027), M_PLAQUE, c)
        lathe(tag + "_bouteille_CO2_10kg",
              [(0, 0.055), (0.07, 0.055), (0.07, 0.70), (0.055, 0.76), (0.03, 0.80),
               (0.02, 0.82), (0.02, 0.86), (0, 0.86)], M_CO2, c, (bxc, byc, 0))
        box(tag + "_robinet_bouteille", (0.04, 0.04, 0.05), (bxc, byc, 0.885), M_INOX, c)
        rod(tag + "_detendeur", (bxc, byc, 0.885), (bxc, byc - 0.08, 0.885), 0.025, M_INOX, c)
        for dx in (-0.035, 0.035):
            rod(tag + "_manometre", (bxc + dx, byc - 0.06, 0.93), (bxc + dx, byc - 0.075, 0.93), 0.022, M_BLANC, c)
        fx, fy = X - side * 0.315, -0.28
        box(tag + "_debitmetre_0_15_Lmin", (0.03, 0.03, 0.16), (fx, fy, 1.05), M_VERRE, c)
        hose(tag + "_tuyau_CO2_a",
             [(bxc, byc - 0.08, 0.885), (bxc + side * 0.10, byc - 0.22, 0.80),
              (fx - side * 0.05, fy - 0.04, 0.88), (fx, fy, 0.97)], 0.005, M_NOIR, c)
        top = pol(0.12, 215, zc + 0.15)
        hose(tag + "_tuyau_CO2_b",
             [(fx, fy, 1.13), (fx, fy, 1.30), (fx + side * 0.05, fy + 0.08, 1.52),
              (top[0], top[1], top[2] + 0.08), top], 0.005, M_NOIR, c)
    return c

# ================================================================== FILTRE F
def filtre(X):
    c = coll("F_Filtre_sous_vide")
    lathe("F_fut_inox_recepteur",
          [(0, 0.04), (0.17, 0.04), (0.19, 0.07), (0.19, 0.40), (0.17, 0.44),
           (0.05, 0.45), (0.05, 0.47), (0.047, 0.47), (0.047, 0.447), (0.168, 0.437),
           (0.187, 0.399), (0.187, 0.071), (0.169, 0.043), (0, 0.043)], M_INOX, c, (X, 0, 0), *CUT)
    lathe("F_collerette_basse", [(0.185, 0.0), (0.195, 0.0), (0.195, 0.075), (0.185, 0.075)], M_INOX, c, (X, 0, 0), *CUT)
    lathe("F_collerette_haute", [(0.185, 0.40), (0.195, 0.40), (0.195, 0.475), (0.185, 0.475)], M_INOX, c, (X, 0, 0), *CUT)
    lathe("F_joint_EPDM", [(0.045, 0.455), (0.062, 0.455), (0.062, 0.474), (0.045, 0.474)], M_NOIR, c, (X, 0, 0))
    lathe("F_cuve_filtrante_30L",
          [(0.047, 0.476), (0.053, 0.471), (0.178, 0.53), (0.178, 0.80), (0.175, 0.80), (0.175, 0.533)],
          M_INOX, c, (X, 0, 0), *CUT)
    rod("F_tole_perforee", (X, 0, 0.545), (X, 0, 0.549), 0.174, M_PLAQUE, c, 64)
    rod("F_toile_filtrante_PP", (X, 0, 0.549), (X, 0, 0.553), 0.174, M_BLANC, c, 64)
    rod("F_gateau_boue_rouge", (X, 0, 0.553), (X, 0, 0.585), 0.162, M_BOUE, c, 64)

    def pol(r, th, z):
        a = math.radians(th)
        return (X + r * math.cos(a), r * math.sin(a), z)
    rod("F_piquage_vide", pol(0.185, 250, 0.36), pol(0.26, 250, 0.36), 0.010, M_INOX, c)
    rod("F_vacuometre", pol(0.23, 250, 0.37), pol(0.23, 250, 0.385), 0.028, M_BLANC, c)
    tx, px, y = X - 0.20, X + 0.18, -0.62
    rod("F_piege_a_liquide_5L", (tx, y, 0.0), (tx, y, 0.26), 0.07, M_VERRE, c, 32)
    rod("F_couvercle_piege", (tx, y, 0.26), (tx, y, 0.275), 0.075, M_NOIR, c, 32)
    entree = pompe_vide(px, y, c)
    p = pol(0.26, 250, 0.36)
    hose("F_tuyau_vide_a", [p, (p[0] - 0.05, p[1] - 0.12, 0.42), (tx - 0.02, y, 0.36), (tx - 0.02, y, 0.275)],
         0.007, M_NOIR, c)
    hose("F_tuyau_vide_b", [(tx + 0.03, y, 0.275), (tx + 0.08, y, 0.35),
                            (entree[0] - 0.03, entree[1], entree[2] + 0.07), entree], 0.007, M_NOIR, c)
    return c

# ================================================================== BROYEUR A0
def broyeur(X):
    c = coll("A0_Broyeur_a_boulets")
    frame("A0_chassis", X, 0.33, 0.20, 0.46, c, rails=(0.15, 0.44))
    box("A0_tablette_moteur", (0.70, 0.44, 0.006), (X, 0, 0.173), M_TOLE, c)
    ZR, ZD = 0.50, 0.625                 # axe des rouleaux, axe du tambour
    for sy in (-1, 1):
        rod("A0_arbre_rouleau_D20", (X - 0.36, sy * 0.10, ZR), (X + 0.40, sy * 0.10, ZR), 0.010, M_INOX, c)
        rod("A0_gaine_caoutchouc", (X - 0.24, sy * 0.10, ZR), (X + 0.24, sy * 0.10, ZR), 0.020, M_NOIR, c)
        for sx in (-1, 1):
            box("A0_palier", (0.04, 0.06, 0.07), (X + sx * 0.33, sy * 0.10, ZR), M_PLAQUE, c)
    rotY = (0, math.radians(90), 0)      # axe de revolution Z -> X
    lathe("A0_tambour_acier_20L",
          [(0, -0.20), (0.14, -0.20), (0.14, 0.20), (0, 0.20), (0, 0.197),
           (0.137, 0.197), (0.137, -0.197), (0, -0.197)],
          M_TOLE, c, (X, 0, ZD), -90, 270, rot=rotY)
    lathe("A0_cerclage_couvercle", [(0.14, 0.18), (0.147, 0.18), (0.147, 0.205), (0.14, 0.205)],
          M_CHASSIS, c, (X, 0, ZD), -90, 270, rot=rotY)
    box("A0_releveur", (0.38, 0.004, 0.02), (X, 0.127, ZD), M_TOLE, c, rot=(math.radians(90), 0, 0))
    rnd = random.Random(7)
    n = 0
    while n < 70:
        r = 0.017 if n < 40 else 0.010
        y, z = rnd.uniform(-0.13, 0.13), rnd.uniform(-0.13, -0.045)
        if math.hypot(y, z) > 0.136 - r:
            continue
        ball("A0_bille_acier" if n < 40 else "A0_bauxite", r,
             (X + rnd.uniform(-0.17, 0.17), y, ZD + z), M_INOX if n < 40 else M_BAUX, c)
        n += 1
    # entrainement
    ym, zm = -0.10, 0.25
    rod("A0_moteur_250W", (X + 0.10, ym, zm), (X + 0.32, ym, zm), 0.06, M_MOTEUR, c, 32)
    box("A0_pattes_moteur", (0.16, 0.14, 0.02), (X + 0.21, ym, 0.186), M_MOTEUR, c)
    rod("A0_arbre_moteur", (X + 0.32, ym, zm), (X + 0.40, ym, zm), 0.008, M_INOX, c)
    rod("A0_poulie_moteur_D50", (X + 0.375, ym, zm), (X + 0.395, ym, zm), 0.025, M_PLAQUE, c, 32)
    rod("A0_poulie_rouleau_D100", (X + 0.375, ym, ZR), (X + 0.395, ym, ZR), 0.05, M_PLAQUE, c, 32)
    for s in (-1, 1):
        rod("A0_courroie", (X + 0.385, ym + s * 0.025, zm), (X + 0.385, ym + s * 0.05, ZR), 0.004, M_NOIR, c, 8)
    return c

# ================================================================== FOUR K
def four(X):
    c = coll("K_Four_de_calcination")
    frame("K_chassis", X, 0.26, 0.26, 0.45, c, rails=(0.43,))
    zb, S, ch = 0.45, 0.56, 0.23          # bas du corps, cote exterieur, chambre
    w = (S - ch) / 2
    zc = zb + S / 2
    box("K_sole_briques", (S, S, w), (X, 0, zb + w / 2), M_BRIQUE, c)
    box("K_voute_briques", (S, S, w), (X, 0, zb + S - w / 2), M_BRIQUE, c)
    for sx in (-1, 1):
        box("K_paroi_briques", (w, S, ch), (X + sx * (ch + w) / 2, 0, zc), M_BRIQUE, c)
        box("K_carcasse_tole", (0.004, S, S), (X + sx * (S / 2 + 0.002), 0, zc), M_TOLE, c)
        for k in range(3):
            z = zc - 0.07 + 0.07 * k
            rod("K_resistance_Kanthal", (X + sx * (ch / 2 - 0.004), -0.26, z),
                (X + sx * (ch / 2 - 0.004), -0.05, z), 0.005, M_RESIST, c, 12)
    depth = 0.25
    box("K_fond_briques", (ch, S - depth, ch), (X, -S / 2 + depth + (S - depth) / 2, zc), M_BRIQUE, c)
    box("K_carcasse_dessus", (S + 0.008, S, 0.004), (X, 0, zb + S + 0.002), M_TOLE, c)
    box("K_carcasse_arriere", (S, 0.004, S), (X, S / 2 + 0.002, zc), M_TOLE, c)
    rod("K_event", (X, -0.15, zb + S), (X, -0.15, zb + S + 0.05), 0.015, M_INOX, c)
    rod("K_thermocouple", (X + 0.06, 0.34, zc + 0.07), (X + 0.06, -0.06, zc + 0.07), 0.004, M_INOX, c)
    box("K_tete_thermocouple", (0.04, 0.05, 0.04), (X + 0.06, 0.34, zc + 0.07), M_COFFRET, c)
    # gazette + poudre
    zs = zc - ch / 2
    box("K_gazette_fond", (0.18, 0.18, 0.008), (X, -0.155, zs + 0.004), M_BRIQUE, c)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        box("K_gazette_bord", (0.008 if sx else 0.18, 0.008 if sy else 0.18, 0.05),
            (X + sx * 0.086, -0.155 + sy * 0.086, zs + 0.025), M_BRIQUE, c)
    box("K_alumine", (0.164, 0.164, 0.03), (X, -0.155, zs + 0.023), M_BLANC, c)
    # porte ouverte a 110 degres, charniere a gauche
    hinge = Vector((X - S / 2, -S / 2, 0))
    a = math.radians(-110)
    Rz = Matrix.Rotation(a, 3, 'Z')
    def door(name, size, off, m):
        p = hinge + Rz @ Vector((off[0], off[1], 0))
        box(name, size, (p.x, p.y, zc + off[2]), m, c, rot=(0, 0, a))
    door("K_porte_briques", (S, 0.08, S), (S / 2, -0.04, 0), M_BRIQUE)
    door("K_porte_tole", (S, 0.006, S), (S / 2, -0.083, 0), M_TOLE)
    door("K_poignee_porte", (0.03, 0.04, 0.14), (S - 0.06, -0.106, 0), M_NOIR)
    # regulateur
    box("K_regulateur_rampes", (0.20, 0.10, 0.26), (X + 0.42, -0.18, zc), M_COFFRET, c)
    box("K_afficheur", (0.08, 0.004, 0.035), (X + 0.42, -0.232, zc + 0.06), M_ECRAN, c)
    box("K_support_regulateur", (0.06, 0.04, 0.04), (X + 0.30, -0.18, zc), M_CHASSIS, c)
    return c

# ================================================================== POMPE A VIDE (version du commerce)
def pompe_vide(px, py, c):
    """Pompe a vide a membrane sans huile, type laboratoire (~30 L/min, -0,08 MPa).
    Renvoie la position de l'embout d'aspiration."""
    L, P, H = 0.28, 0.16, 0.19
    z0 = 0.012
    zt = z0 + H
    fy = py - P / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod("F_pompe_pied", (px + sx * 0.11, py + sy * 0.055, 0), (px + sx * 0.11, py + sy * 0.055, z0),
                0.012, M_NOIR, c, 16)
    box("F_pompe_socle", (L, P, 0.06), (px, py, z0 + 0.03), M_PANNEAU, c)
    box("F_pompe_capot", (L - 0.004, P - 0.004, H - 0.06), (px, py, z0 + 0.06 + (H - 0.06) / 2), M_FOUR, c)
    # poignee de transport
    for sx in (-1, 1):
        box("F_pompe_poignee_pied", (0.02, 0.03, 0.035), (px + sx * 0.07, py, zt + 0.0175), M_NOIR, c)
    box("F_pompe_poignee", (0.16, 0.03, 0.016), (px, py, zt + 0.043), M_NOIR, c)
    # manometre de vide en facade
    gx, gz = px + 0.065, z0 + 0.125
    rod("F_pompe_manometre_boitier", (gx, fy, gz), (gx, fy - 0.022, gz), 0.034, M_INOX, c, 32)
    rod("F_pompe_manometre_cadran", (gx, fy - 0.022, gz), (gx, fy - 0.0225, gz), 0.029, M_BLANC, c, 32)
    for i in range(9):              # graduations
        a = math.radians(-135 + i * 33.75)
        box("F_pompe_graduation", (0.0012, 0.0006, 0.005),
            (gx + 0.024 * math.sin(a), fy - 0.0229, gz + 0.024 * math.cos(a)), M_NOIR, c, rot=(0, a, 0))
    a = math.radians(-60)           # aiguille sur -0,06 MPa environ
    box("F_pompe_aiguille", (0.0015, 0.0008, 0.024),
        (gx + 0.010 * math.sin(a), fy - 0.0232, gz + 0.010 * math.cos(a)), M_ROUGE, c, rot=(0, a, 0))
    rod("F_pompe_axe_aiguille", (gx, fy - 0.0225, gz), (gx, fy - 0.025, gz), 0.003, M_NOIR, c, 12)
    # interrupteur, voyant, regulation du vide
    box("F_pompe_interrupteur", (0.028, 0.012, 0.018), (px - 0.09, fy - 0.006, z0 + 0.03), M_ROUGE, c)
    rod("F_pompe_voyant", (px - 0.05, fy, z0 + 0.03), (px - 0.05, fy - 0.006, z0 + 0.03), 0.005, M_ECRAN_V, c, 12)
    rod("F_pompe_bouton_reglage", (px - 0.06, fy, z0 + 0.125), (px - 0.06, fy - 0.018, z0 + 0.125), 0.014, M_NOIR, c, 24)
    box("F_pompe_plaque", (0.07, 0.001, 0.03), (px - 0.06, fy - 0.0005, z0 + 0.085), M_INOX, c)
    # aerations laterales
    for i in range(6):
        box("F_pompe_ouie", (0.001, 0.09, 0.006), (px - L / 2 - 0.0005, py, z0 + 0.08 + i * 0.016), M_NOIR, c)
        box("F_pompe_ouie", (0.001, 0.09, 0.006), (px + L / 2 + 0.0005, py, z0 + 0.08 + i * 0.016), M_NOIR, c)
    # embouts d'aspiration (dessus) et de refoulement (cote droit)
    ex, ey = px - 0.09, py - 0.035
    rod("F_pompe_ecrou_aspiration", (ex, ey, zt), (ex, ey, zt + 0.012), 0.011, M_INOX, c, 6)
    rod("F_pompe_embout_aspiration", (ex, ey, zt + 0.012), (ex, ey, zt + 0.04), 0.0055, M_INOX, c, 16)
    rod("F_pompe_embout_refoulement", (px + L / 2, py + 0.03, z0 + 0.04), (px + L / 2 + 0.03, py + 0.03, z0 + 0.04),
        0.0055, M_INOX, c, 16)
    hose("F_pompe_cable", [(px + 0.08, py + P / 2, z0 + 0.03), (px + 0.10, py + P / 2 + 0.10, 0.006),
                           (px + 0.30, py + 0.25, 0.006)], 0.004, M_NOIR, c)
    return (ex, ey, zt + 0.04)


# ================================================================== BROYEUR A0 (version realiste)
def broyeur_reel(X):
    """Broyeur a boulets sur rouleaux : fut acier 20 L ferme pose sur deux rouleaux
    caoutchoutes, motoreducteur sur l'etagere, transmission sous carter de protection."""
    c = coll("A0_Broyeur_a_boulets")
    frame("A0_chassis", X, 0.33, 0.20, 0.46, c, rails=(0.15, 0.44))
    box("A0_tablette_moteur", (0.70, 0.44, 0.006), (X, 0, 0.173), M_TOLE, c)
    ZR, ZD, RD = 0.50, 0.625, 0.14

    # rouleaux et paliers a semelle
    for sy in (-1, 1):
        y = sy * 0.10
        rod("A0_arbre_rouleau_D20", (X - 0.37, y, ZR), (X + 0.40, y, ZR), 0.010, M_INOX, c)
        rod("A0_gaine_caoutchouc", (X - 0.24, y, ZR), (X + 0.24, y, ZR), 0.020, M_NOIR, c)
        for sx in (-1, 1):
            x = X + sx * 0.33
            box("A0_palier_semelle", (0.04, 0.11, 0.014), (x, y, 0.467), M_PLAQUE, c)
            box("A0_palier_corps", (0.034, 0.05, 0.03), (x, y, 0.485), M_PLAQUE, c)
            rod("A0_palier_logement", (x - 0.018, y, ZR), (x + 0.018, y, ZR), 0.028, M_PLAQUE, c, 32)
            rod("A0_palier_graisseur", (x, y, ZR + 0.028), (x, y, ZR + 0.038), 0.003, M_INOX, c, 8)
            for dy in (-0.04, 0.04):
                rod("A0_palier_boulon", (x, y + dy, 0.474), (x, y + dy, 0.482), 0.006, M_INOX, c, 6)

    # fut acier 20 L ferme (axe selon X), avec bourrelets de roulement et cercle de fermeture
    rotY = (0, math.radians(90), 0)
    lathe("A0_fut_acier_20L", [(0, -0.20), (RD, -0.20), (RD, 0.195), (RD - 0.002, 0.195),
                               (RD - 0.002, -0.197), (0, -0.197)], M_FUT, c, (X, 0, ZD), rot=rotY)   # fut creux
    for zz in (-0.20, 0.085, -0.085):
        circ = [(RD + 0.004 * math.cos(t), zz + 0.004 * math.sin(t)) for t in [i * math.tau / 8 for i in range(8)]]
        lathe("A0_bourrelet_fut", circ, M_FUT, c, (X, 0, ZD), rot=rotY)
    lathe("A0_couvercle", [(0, 0.195), (RD + 0.004, 0.195), (RD + 0.004, 0.205), (0.02, 0.212), (0, 0.212)],
          M_FUT, c, (X, 0, ZD), rot=rotY)
    circ = [(RD + 0.008 + 0.006 * math.cos(t), 0.199 + 0.006 * math.sin(t)) for t in [i * math.tau / 10 for i in range(10)]]
    lathe("A0_cercle_fermeture", circ, M_INOX, c, (X, 0, ZD), rot=rotY)
    box("A0_levier_cercle", (0.03, 0.02, 0.05), (X + 0.199, -0.02, ZD + RD + 0.02), M_INOX, c)

    # motoreducteur sur l'etagere
    ym, zm = -0.10, 0.25
    rod("A0_capot_ventilateur", (X + 0.0, ym, zm), (X + 0.03, ym, zm), 0.058, M_MOTEUR, c, 32)
    rod("A0_moteur_250W", (X + 0.03, ym, zm), (X + 0.19, ym, zm), 0.052, M_MOTEUR, c, 32)
    for k in range(18):             # ailettes de refroidissement longitudinales
        a = k * math.tau / 18
        if abs(math.cos(a)) > 0.9 and math.cos(a) < 0:
            continue                    # pas d'ailette sous le moteur (pattes)
        box("A0_ailette_moteur", (0.15, 0.003, 0.012),
            (X + 0.11, ym + 0.056 * math.sin(a), zm + 0.056 * math.cos(a)), M_MOTEUR, c, rot=(-a, 0, 0))
    box("A0_boite_a_bornes", (0.06, 0.055, 0.035), (X + 0.11, ym, zm + 0.07), M_MOTEUR, c)
    box("A0_reducteur", (0.10, 0.11, 0.12), (X + 0.24, ym, zm), M_MOTEUR, c)
    box("A0_pattes_moteur", (0.28, 0.12, 0.014), (X + 0.15, ym, 0.183), M_MOTEUR, c)
    for x in (X + 0.10, X + 0.24):
        box("A0_support_patte", (0.03, 0.09, zm - 0.06 - 0.19), (x, ym, (zm - 0.06 + 0.19) / 2), M_MOTEUR, c)
    rod("A0_arbre_sortie", (X + 0.29, ym, zm), (X + 0.40, ym, zm), 0.009, M_INOX, c)

    # carter de protection jaune sur la transmission (poulies + courroie)
    xg0, xg1 = X + 0.365, X + 0.415
    for z in (zm, ZR):
        rod("A0_carter_courroie", (xg0, ym, z), (xg1, ym, z), 0.065, M_JAUNE, c, 32)
    box("A0_carter_courroie", (xg1 - xg0, 0.13, ZR - zm), ((xg0 + xg1) / 2, ym, (zm + ZR) / 2), M_JAUNE, c)

    # boitier marche / arret sur le pied avant gauche
    bx, by, bz = X - 0.33, -0.245, 0.33
    box("A0_boitier_commande", (0.08, 0.05, 0.11), (bx, by, bz), M_COFFRET, c)
    rod("A0_bouton_marche", (bx, by - 0.025, bz + 0.025), (bx, by - 0.035, bz + 0.025), 0.011, M_ECRAN_V, c, 16)
    rod("A0_bouton_arret", (bx, by - 0.025, bz - 0.02), (bx, by - 0.037, bz - 0.02), 0.013, M_ROUGE, c, 16)
    hose("A0_cable_moteur", [(bx, by, bz - 0.055), (bx + 0.05, by + 0.04, 0.24),
                             (X + 0.11, ym - 0.06, zm + 0.10), (X + 0.11, ym, zm + 0.0875)], 0.004, M_NOIR, c)
    return c


# ================================================================== FOUR K (version du commerce)
def helice(name, p0, length, r, pitch, wire, m, c):
    """Spirale de fil chauffant le long de Y (resistance de four)."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    n = int(length / pitch * 12)
    sp.points.add(n)
    for i in range(n + 1):
        a = i * math.tau / 12
        sp.points[i].co = (p0[0] + r * math.cos(a), p0[1] + i * length / n, p0[2] + r * math.sin(a), 1)
    cu.bevel_depth = wire
    cu.bevel_resolution = 2
    cu.materials.append(m)
    ob = bpy.data.objects.new(name, cu)
    c.objects.link(ob)
    return ob


def four_moufle(X):
    """Four a moufle 1200 °C de laboratoire, tel qu'on l'achete (Chine) :
    caisson en tole peinte, chambre en fibre ceramique avec resistances en spirale,
    colonne de commande a droite, porte a charniere a gauche. Pose sur une table."""
    c = coll("K_Four_de_calcination")

    # table en corniere + plateau
    frame("K_table", X, 0.30, 0.26, 0.45, c, rails=(0.12, 0.43))
    box("K_plateau_table", (0.64, 0.56, 0.008), (X, 0, 0.454), M_CHASSIS, c)

    z0, H, D = 0.478, 0.50, 0.46
    y0, y1 = -D / 2, D / 2
    zt = z0 + H
    xc, W = X - 0.08, 0.40          # partie chambre
    xk, WK = X + 0.20, 0.16         # colonne de commande
    xa, xb = xc - W / 2, xk + WK / 2
    t = 0.0015                      # epaisseur de tole

    def blk(name, xa_, xb_, ya_, yb_, za_, zb_, m):
        return box(name, (xb_ - xa_, yb_ - ya_, zb_ - za_),
                   ((xa_ + xb_) / 2, (ya_ + yb_) / 2, (za_ + zb_) / 2), m, c)

    for sx in (-1, 1):
        for sy in (-1, 1):
            rod("K_pied_caoutchouc", (X + sx * 0.24, sy * 0.19, 0.458), (X + sx * 0.24, sy * 0.19, z0),
                0.015, M_NOIR, c, 16)

    # chambre 230 x 230 x 300 mm en fibre ceramique
    cw, ch, cd = 0.23, 0.23, 0.30
    cz0 = z0 + 0.15
    cx0, cx1 = xc - cw / 2, xc + cw / 2
    cy1 = y0 + cd
    fx0, fx1 = xa + t, xc + W / 2
    blk("K_fibre_sole", fx0, fx1, y0 + t, cy1, z0 + t, cz0, M_FIBRE)
    blk("K_fibre_voute", fx0, fx1, y0 + t, cy1, cz0 + ch, zt - t, M_FIBRE)
    blk("K_fibre_gauche", fx0, cx0, y0 + t, cy1, cz0, cz0 + ch, M_FIBRE)
    blk("K_fibre_droite", cx1, fx1, y0 + t, cy1, cz0, cz0 + ch, M_FIBRE)
    blk("K_fibre_fond", fx0, fx1, cy1, y1 - t, z0 + t, zt - t, M_FIBRE)

    # resistances en spirale noyees dans les parois laterales
    for xw in (cx0 + 0.003, cx1 - 0.003):
        for dz in (0.05, 0.115, 0.18):
            helice("K_resistance_Kanthal", (xw, y0 + 0.03, cz0 + dz), cd - 0.05, 0.006, 0.005,
                   0.0011, M_RESIST, c)

    # caisson en tole peinte (blanc-gris)
    blk("K_coque_dessus", xa, xb, y0, y1, zt - t, zt, M_FOUR)
    blk("K_coque_dessous", xa, xb, y0, y1, z0, z0 + t, M_FOUR)
    blk("K_coque_gauche", xa, xa + t, y0, y1, z0, zt, M_FOUR)
    blk("K_coque_droite", xb - t, xb, y0, y1, z0, zt, M_FOUR)
    blk("K_coque_arriere", xa, xb, y1 - t, y1, z0, zt, M_FOUR)
    blk("K_facade_bas", xa, xc + W / 2, y0, y0 + t, z0, cz0, M_FOUR)
    blk("K_facade_haut", xa, xc + W / 2, y0, y0 + t, cz0 + ch, zt, M_FOUR)
    blk("K_facade_gauche", xa, cx0, y0, y0 + t, cz0, cz0 + ch, M_FOUR)
    blk("K_facade_droite", cx1, xc + W / 2, y0, y0 + t, cz0, cz0 + ch, M_FOUR)
    e = 0.012                       # cadre inox autour de l'ouverture
    blk("K_cadre_ouverture", cx0 - e, cx1 + e, y0 - 0.003, y0, cz0 + ch, cz0 + ch + e, M_INOX)
    blk("K_cadre_ouverture", cx0 - e, cx1 + e, y0 - 0.003, y0, cz0 - e, cz0, M_INOX)
    blk("K_cadre_ouverture", cx0 - e, cx0, y0 - 0.003, y0, cz0, cz0 + ch, M_INOX)
    blk("K_cadre_ouverture", cx1, cx1 + e, y0 - 0.003, y0, cz0, cz0 + ch, M_INOX)
    for i in range(7):              # ouies d'aeration sur le cote droit
        blk("K_ouie_aeration", xb, xb + 0.001, -0.10, 0.10, z0 + 0.10 + i * 0.03, z0 + 0.108 + i * 0.03, M_NOIR)

    # colonne de commande
    py = y0 - 0.003
    blk("K_facade_commande", xc + W / 2, xb, py, y0 + t, z0, zt, M_PANNEAU)
    zr = zt - 0.11
    box("K_regulateur_PID_96x96", (0.096, 0.012, 0.096), (xk, py - 0.006, zr), M_NOIR, c)
    for nom, txt, z, hz, m in (("K_afficheur_PV", "1050", zr + 0.022, 0.024, M_ECRAN),
                               ("K_afficheur_SV", "1050", zr - 0.007, 0.017, M_ECRAN_V)):
        box(nom + "_fond", (0.066, 0.002, hz), (xk, py - 0.0125, z), M_NOIR, c)
        cu = bpy.data.curves.new(nom, 'FONT')
        cu.body = txt
        cu.size = hz * 0.95
        cu.align_x = 'CENTER'
        cu.align_y = 'CENTER'
        cu.materials.append(m)
        ob = bpy.data.objects.new(nom, cu)
        ob.location = (xk, py - 0.0137, z)
        ob.rotation_euler = (math.pi / 2, 0, 0)
        c.objects.link(ob)
    for i in range(4):
        box("K_bouton", (0.012, 0.004, 0.008), (xk - 0.027 + i * 0.018, py - 0.013, zr - 0.032), M_COFFRET, c)
    box("K_interrupteur", (0.032, 0.014, 0.022), (xk, py - 0.007, zr - 0.13), M_ROUGE, c)
    rod("K_voyant_marche", (xk - 0.03, py, zr - 0.19), (xk - 0.03, py - 0.008, zr - 0.19), 0.007, M_ECRAN_V, c, 16)
    rod("K_voyant_chauffe", (xk + 0.03, py, zr - 0.19), (xk + 0.03, py - 0.008, zr - 0.19), 0.007, M_ROUGE, c, 16)
    box("K_plaque_signaletique", (0.10, 0.002, 0.04), (xk, py - 0.001, z0 + 0.07), M_INOX, c)

    # dessus : evacuation des vapeurs, thermocouple ; arriere : cable
    yc = (y0 + cy1) / 2
    rod("K_evacuation_vapeur", (xc, yc, zt - 0.06), (xc, yc, zt + 0.05), 0.011, M_INOX, c)
    rod("K_thermocouple", (xc + 0.07, cy1 - 0.04, cz0 + ch - 0.04), (xc + 0.07, cy1 - 0.04, zt + 0.03),
        0.004, M_BLANC, c)
    box("K_tete_thermocouple", (0.03, 0.03, 0.025), (xc + 0.07, cy1 - 0.04, zt + 0.042), M_NOIR, c)
    hose("K_cable_alimentation", [(xk, y1, z0 + 0.08), (xk, y1 + 0.12, z0 + 0.02),
                                  (xk + 0.10, y1 + 0.30, 0.30), (xk + 0.15, y1 + 0.45, 0.01)], 0.006, M_NOIR, c)

    # creuset (gazette) + alumine sur la sole
    gx, gy = xc, yc
    box("K_gazette_fond", (0.16, 0.16, 0.008), (gx, gy, cz0 + 0.004), M_BRIQUE, c)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        box("K_gazette_bord", (0.008 if sx else 0.16, 0.008 if sy else 0.16, 0.045),
            (gx + sx * 0.076, gy + sy * 0.076, cz0 + 0.0225), M_BRIQUE, c)
    box("K_alumine", (0.144, 0.144, 0.025), (gx, gy, cz0 + 0.0205), M_BLANC, c)

    # porte a charniere a gauche, ouverte a 100 degres
    zd0, zd1 = cz0 - 0.07, cz0 + ch + 0.07
    zm = (zd0 + zd1) / 2
    hinge = Vector((xa, y0, 0))
    a = math.radians(-100)
    Rz = Matrix.Rotation(a, 3, 'Z')

    def door(name, size, off, m):
        p = hinge + Rz @ Vector((off[0], off[1], 0))
        box(name, size, (p.x, p.y, zm + off[2]), m, c, rot=(0, 0, a))

    door("K_porte_caisson", (W, 0.075, zd1 - zd0), (W / 2, -0.0405, 0), M_FOUR)
    door("K_porte_bouchon_fibre", (cw - 0.006, 0.04, ch - 0.006), (W / 2, 0.017, 0), M_FIBRE)
    door("K_porte_joint", (cw + 0.03, 0.004, ch + 0.03), (W / 2, -0.001, 0), M_FIBRE)
    for dz in (-0.06, 0.06):
        door("K_poignee_porte", (0.012, 0.03, 0.012), (W - 0.04, -0.093, dz), M_NOIR)
    door("K_poignee_porte", (0.016, 0.016, 0.15), (W - 0.04, -0.112, 0), M_NOIR)
    for dz in (-0.10, 0.10):
        rod("K_charniere", (xa - 0.004, y0 - 0.004, zm + dz - 0.03), (xa - 0.004, y0 - 0.004, zm + dz + 0.03),
            0.007, M_INOX, c, 16)
    return c


# ================================================================== SCENE
X_A0, X_R1, X_F, X_R2, X_K = -2.35, -0.85, 0.0, 0.85, 2.45

broyeur_reel(X_A0)
reactor("R1_Attaque", X_R1, +1, cut=True, co2=False, liq_rgb=(0.40, 0.10, 0.05), liq_alpha=0.95)
filtre(X_F)
reactor("R2_Precipitation", X_R2, -1, cut=True, co2=True)
four_moufle(X_K)

env = coll("Atelier")
box("Sol", (7.6, 3.6, 0.02), (0.1, 0, -0.011), M_SOL, env)
box("Bac_retention_fond", (2.50, 0.84, 0.006), (0, 0, 0.003), M_BAC, env)
for sy in (-1, 1):
    box("Bac_retention_bord", (2.50, 0.006, 0.10), (0, sy * 0.42, 0.05), M_BAC, env)
for sx in (-1, 1):
    box("Bac_retention_bord", (0.006, 0.84, 0.10), (sx * 1.25, 0, 0.05), M_BAC, env)
box("Regle_1m", (1.0, 0.03, 0.01), (0, -1.15, 0.005), M_BLANC, env)
label("Txt_1m", "1 m", (0, -1.15, 0.03), 0.07, env)
rod("Repere_personne_corps", (-3.35, -0.2, 0), (-3.35, -0.2, 1.52), 0.13, M_REPERE, env, 24)
ball("Repere_personne_tete", 0.115, (-3.35, -0.2, 1.635), M_REPERE, env)
label("Txt_personne", "1,75 m", (-3.35, -0.2, 1.80), 0.07, env)

for nom, txt, x, z in (
        ("Txt_A0", "A0  BROYEUR\nbauxite < 250 µm", X_A0, 1.10),
        ("Txt_R1", "R1  ATTAQUE\nsoude 100 °C, 2 h", X_R1, 1.95),
        ("Txt_F", "F  FILTRE\nsous vide", X_F, 1.10),
        ("Txt_R2", "R2  PRECIPITATION\nCO2, 75 °C", X_R2, 1.95),
        ("Txt_K", "K  FOUR\n1050 °C", X_K, 1.30)):
    label(nom, txt, (x, 0.30, z), 0.095, env)

# camera, lumieres, monde
cam_d = bpy.data.cameras.new("Camera")
cam_d.lens = 35
cam = bpy.data.objects.new("Camera", cam_d)
scene.collection.objects.link(cam)
cam.location = (0.4, -7.7, 2.9)
cam.rotation_euler = (Vector((0.05, 0, 0.85)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

sun_d = bpy.data.lights.new("Soleil", 'SUN')
sun_d.energy = 2.2
sun = bpy.data.objects.new("Soleil", sun_d)
sun.rotation_euler = (math.radians(50), 0, math.radians(25))
scene.collection.objects.link(sun)
ar_d = bpy.data.lights.new("Appoint", 'AREA')
ar_d.energy = 600
ar_d.size = 4
ar = bpy.data.objects.new("Appoint", ar_d)
ar.location = (-1.5, -4.5, 3.5)
ar.rotation_euler = (Vector((0, 0, 0.8)) - Vector(ar.location)).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(ar)

world = scene.world or bpy.data.worlds.new("Monde")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
if bg:
    bg.inputs[0].default_value = (0.42, 0.48, 0.58, 1)
    bg.inputs[1].default_value = 0.45
try:
    scene.view_settings.view_transform = 'Standard'
except TypeError:
    pass

scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
print("Scene construite :", len(bpy.data.objects), "objets")
