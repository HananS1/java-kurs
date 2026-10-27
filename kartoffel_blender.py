"""
KARTOFFEL – 1.000 SCHNITTE   (Blender 4.2 oder neuer)

So geht's:
  1. Die Datei "kartoffel_sound.wav" in deinen Downloads-Ordner legen (oder ORDNER unten ändern).
  2. Blender öffnen -> oben Reiter "Scripting" -> "Öffnen" -> diese Datei -> ▶ (Skript ausführen).
  3. Menü "Rendern" -> "Animation rendern" (Strg+F12).
  Das fertige Video (mit Ton) landet als MP4 im ORDNER.
"""
import bpy, bmesh, math, os
import numpy as np

# ---------------- Einstellungen ----------------
ORDNER = os.path.join(os.path.expanduser("~"), "Downloads")
SOUND = "kartoffel_sound.wav"
VIDEO = "kartoffel_1000_schnitte_blender.mp4"
ENGINE = "EEVEE"          # "EEVEE" (schnell) oder "CYCLES" (fotorealistisch, langsamer)
FPS = 30
RES = (1080, 1920)

# ---------------- Szene / Ablauf (identisch zum Sound-Timing) ----------------
A, B, C = 4.2, 2.5, 2.8
CY = B * 0.9
PILE_H = 2.6
STAGES = [dict(N=10, P=5, pass_=0.30), dict(N=50, P=25, pass_=0.15), dict(N=100, P=25, pass_=0.155),
          dict(N=250, P=25, pass_=0.165), dict(N=500, P=25, pass_=0.18), dict(N=1000, P=25, pass_=0.20)]
INTRO, SWITCH, COLLAPSE, HOLD = 0.35, 0.25, 0.9, 0.6
KNIFE_TOP = 5.3
PX = 0.012                # ungefähre Pixelgröße in Weltkoordinaten (für feine Schnittlinien)


def V(x, y, z):
    """three.js-Koordinaten (y oben) -> Blender (z oben)."""
    return (x, -z, y)


def clamp(v, a, b): return min(b, max(a, v))
def lerp(a, b, t): return a + (b - a) * t
def ease_in(t): return t * t
def ease_out(t): return 1 - (1 - t) ** 3
def smoothstep(a, b, x): t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def srgb(r, g, b, a=1.0): return (r ** 2.2, g ** 2.2, b ** 2.2, a)


def shape_noise(dx, dy, dz):
    return (0.05 * np.sin(6.3 * dx + 0.7) * np.cos(5.1 * dz + 1.3)
            + 0.03 * np.sin(5 * dy + 4 * dx)
            + 0.025 * np.sin(7 * dz + 2) * np.sin(6 * dx + 1))


def potato_radius(dx, dy, dz):
    e = 1 / np.sqrt((dx / A) ** 2 + (dy / B) ** 2 + (dz / C) ** 2)
    return e * (1 + shape_noise(dx, dy, dz))


def inside_potato(x, y, z):
    qy = y - CY
    L = np.sqrt(x * x + qy * qy + z * z) + 1e-9
    return (y >= 0.02) & (L <= potato_radius(x / L, qy / L, z / L))


def pile_map(x, y, z, c):
    s = np.clip(1 - (x / A) ** 2 - (z / C) ** 2, 0.0001, 1)
    half = B * np.sqrt(s)
    top, bot = CY + half, np.maximum(0, CY - half)
    frac = np.clip((y - bot) / np.maximum(top - bot, 1e-4), 0, 1)
    return x + (x * 1.2 - x) * c, y + (frac * PILE_H * s ** 0.6 - y) * c, z + (z * 1.25 - z) * c


# ---------------- aufräumen ----------------
for h in list(bpy.app.handlers.frame_change_pre):
    if getattr(h, "__name__", "") == "kartoffel_frame":
        bpy.app.handlers.frame_change_pre.remove(h)
sc = bpy.context.scene
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
rng = np.random.default_rng(5)


# ---------------- Node-Helfer ----------------
class NB:
    def __init__(self, mat):
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.new('ShaderNodeOutputMaterial')
        self.bsdf = self.new('ShaderNodeBsdfPrincipled')
        self.link(self.bsdf.outputs['BSDF'], self.out.inputs['Surface'])

    def new(self, t, **kw):
        n = self.nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def link(self, v, inp):
        if isinstance(v, (int, float)):
            inp.default_value = v
        elif isinstance(v, tuple):
            inp.default_value = v
        else:
            self.nt.links.new(v, inp)

    def m(self, op, a, b=None, c=None, clamp_=False):
        n = self.new('ShaderNodeMath', operation=op, use_clamp=clamp_)
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def val(self, name, v=0.0):
        n = self.new('ShaderNodeValue', name=name, label=name)
        n.outputs[0].default_value = v
        return n.outputs[0]

    def smooth(self, x, a, b):
        n = self.new('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP', clamp=True)
        self.link(x, n.inputs['Value']); self.link(a, n.inputs['From Min']); self.link(b, n.inputs['From Max'])
        return n.outputs['Result']

    def mix(self, f, a, b):
        n = self.new('ShaderNodeMix', data_type='RGBA')
        ins = [s for s in n.inputs if s.type == 'RGBA']
        self.link(f, n.inputs[0]); self.link(a, ins[0]); self.link(b, ins[1])
        return [s for s in n.outputs if s.type == 'RGBA'][0]

    def vmath(self, op, a, b=None):
        n = self.new('ShaderNodeVectorMath', operation=op)
        self.link(a, n.inputs[0])
        if b is not None:
            self.link(b, n.inputs[1])
        return n.outputs[0]

    def rgb_scale(self, col, s):
        n = self.new('ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY')
        ins = [x for x in n.inputs if x.type == 'RGBA']
        n.inputs[0].default_value = 1.0
        self.link(col, ins[0])
        cmb = self.new('ShaderNodeCombineColor')
        for i in range(3):
            self.link(s, cmb.inputs[i])
        self.link(cmb.outputs[0], ins[1])
        return [x for x in n.outputs if x.type == 'RGBA'][0]

    def skin(self, coord):
        n1 = self.new('ShaderNodeTexNoise'); self.link(coord, n1.inputs['Vector'])
        n1.inputs['Scale'].default_value = 2.0; n1.inputs['Detail'].default_value = 4
        r1 = self.new('ShaderNodeValToRGB'); self.link(n1.outputs['Fac'], r1.inputs[0])
        r1.color_ramp.elements[0].position, r1.color_ramp.elements[0].color = 0.3, srgb(0.55, 0.37, 0.19)
        r1.color_ramp.elements[1].position, r1.color_ramp.elements[1].color = 0.7, srgb(0.72, 0.53, 0.31)
        n2 = self.new('ShaderNodeTexNoise'); self.link(coord, n2.inputs['Vector'])
        n2.inputs['Scale'].default_value = 1.3; n2.inputs['Detail'].default_value = 0
        eye = self.smooth(n2.outputs['Fac'], 0.72, 0.76)
        col = self.mix(self.m('MULTIPLY', eye, 0.7), r1.outputs['Color'], srgb(0.36, 0.23, 0.11))
        wn = self.new('ShaderNodeTexWhiteNoise', noise_dimensions='3D')
        self.link(self.vmath('SNAP', coord, (1 / 45, 1 / 45, 1 / 45)), wn.inputs['Vector'])
        return self.rgb_scale(col, self.m('MULTIPLY_ADD', wn.outputs['Value'], 0.2, 0.9))


FLESH = srgb(1.0, 0.86, 0.47)

# ---------------- Kartoffel-Material ----------------
mat_potato = bpy.data.materials.get("Kartoffel") or bpy.data.materials.new("Kartoffel")
nb = NB(mat_potato)
U = {}
for k in ["uSx", "uSz", "uNx", "uNz", "uPassX", "uPassZ", "uP", "uWx", "uWz", "uCovX", "uCovZ",
          "uDenseX", "uDenseZ", "uPile", "uCellX", "uCellY", "uCellZ"]:
    U[k] = nb.val(k, 1.0 if k.startswith("uCell") or k == "uP" else 0.0)
tc = nb.new('ShaderNodeTexCoord')
geo = nb.new('ShaderNodeNewGeometry')
sep = nb.new('ShaderNodeSeparateXYZ'); nb.link(geo.outputs['Position'], sep.inputs[0])
skin_col = nb.skin(tc.outputs['Object'])


def cut_line(coord, x0, s, n, passes, w, cov, dense):
    k = nb.m('FLOOR', nb.m('ADD', nb.m('DIVIDE', nb.m('SUBTRACT', coord, x0), s), 0.5))
    valid = nb.m('MULTIPLY', nb.m('GREATER_THAN', k, 0.5), nb.m('LESS_THAN', k, nb.m('ADD', n, 0.5)))
    active = nb.m('LESS_THAN', nb.m('FLOORED_MODULO', nb.m('SUBTRACT', k, 1), U["uP"]), nb.m('SUBTRACT', passes, 0.5))
    d = nb.m('ABSOLUTE', nb.m('SUBTRACT', coord, nb.m('MULTIPLY_ADD', k, s, x0)))
    a = nb.m('SUBTRACT', 1, nb.smooth(d, nb.m('SUBTRACT', w, PX), nb.m('ADD', w, PX)))
    line = nb.m('ADD', nb.m('MULTIPLY', a, nb.m('SUBTRACT', 1, dense)), nb.m('MULTIPLY', cov, dense))
    return nb.m('MULTIPLY', line, nb.m('MULTIPLY', valid, active))


three_z = nb.m('MULTIPLY', sep.outputs['Y'], -1)
lx = cut_line(sep.outputs['X'], -A, U["uSx"], U["uNx"], U["uPassX"], U["uWx"], U["uCovX"], U["uDenseX"])
lz = cut_line(three_z, -C, U["uSz"], U["uNz"], U["uPassZ"], U["uWz"], U["uCovZ"], U["uDenseZ"])
col = nb.mix(nb.m('MAXIMUM', lx, lz), skin_col, tuple(c * 0.88 for c in FLESH[:3]) + (1,))
cell_size = nb.new('ShaderNodeCombineXYZ')
nb.link(U["uCellX"], cell_size.inputs[0]); nb.link(U["uCellZ"], cell_size.inputs[1]); nb.link(U["uCellY"], cell_size.inputs[2])
cell = nb.vmath('FLOOR', nb.vmath('DIVIDE', geo.outputs['Position'], cell_size.outputs[0]))
wn1 = nb.new('ShaderNodeTexWhiteNoise', noise_dimensions='3D'); nb.link(cell, wn1.inputs['Vector'])
wn2 = nb.new('ShaderNodeTexWhiteNoise', noise_dimensions='3D'); nb.link(nb.vmath('ADD', cell, (17.3, 17.3, 17.3)), wn2.inputs['Vector'])
pile_col = nb.rgb_scale(FLESH, nb.m('MULTIPLY_ADD', wn1.outputs['Value'], 0.28, 0.80))
pile_col = nb.mix(nb.m('LESS_THAN', wn2.outputs['Value'], 0.07), pile_col, skin_col)
col = nb.mix(U["uPile"], col, pile_col)
nb.link(col, nb.bsdf.inputs['Base Color'])
nb.bsdf.inputs['Roughness'].default_value = 0.75

# ---------------- Würfel-Material (Schale nur auf Außenseiten) ----------------
mat_cube = bpy.data.materials.get("KartoffelWuerfel") or bpy.data.materials.new("KartoffelWuerfel")
cb = NB(mat_cube)
attr_mask = cb.new('ShaderNodeAttribute', attribute_type='INSTANCER', attribute_name='mask')
attr_shade = cb.new('ShaderNodeAttribute', attribute_type='INSTANCER', attribute_name='shade')
g2 = cb.new('ShaderNodeNewGeometry')
attr_face = cb.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='facebit')
is_skin = cb.m('FLOORED_MODULO', cb.m('FLOOR', cb.m('DIVIDE', attr_mask.outputs['Fac'], cb.m('MAXIMUM', attr_face.outputs['Fac'], 1))), 2)
cc = cb.mix(cb.m('MINIMUM', is_skin, 1), cb.rgb_scale(FLESH, attr_shade.outputs['Fac']), cb.skin(g2.outputs['Position']))
cb.link(cc, cb.bsdf.inputs['Base Color'])
cb.bsdf.inputs['Roughness'].default_value = 0.7


def simple_mat(name, color, metal=0.0, rough=0.5, alpha=1.0, emit=False):
    mt = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    n = NB(mt)
    if emit:
        n.nt.nodes.remove(n.bsdf)
        e = n.new('ShaderNodeEmission'); e.inputs['Color'].default_value = color; e.inputs['Strength'].default_value = 1.0
        n.link(e.outputs[0], n.out.inputs['Surface'])
    else:
        n.bsdf.inputs['Base Color'].default_value = color
        n.bsdf.inputs['Metallic'].default_value = metal
        n.bsdf.inputs['Roughness'].default_value = rough
        n.bsdf.inputs['Alpha'].default_value = alpha
    if alpha < 1:
        if hasattr(mt, "surface_render_method"):
            mt.surface_render_method = 'BLENDED'
        if hasattr(mt, "blend_method"):
            try: mt.blend_method = 'BLEND'
            except Exception: pass
    return mt


mat_steel = simple_mat("Klinge", srgb(0.86, 0.88, 0.9), metal=1.0, rough=0.2)
mat_ghost = simple_mat("KlingeGeist", srgb(0.88, 0.9, 0.93), metal=0.6, rough=0.25, alpha=0.25)
mat_handle = simple_mat("Griff", srgb(0.17, 0.11, 0.08), rough=0.45)
mat_rivet = simple_mat("Niete", srgb(0.75, 0.77, 0.8), metal=1.0, rough=0.3)
mat_counter = simple_mat("Arbeitsplatte", srgb(0.95, 0.94, 0.91), rough=0.6)
mat_white = simple_mat("TextWeiss", (1, 1, 1, 1), emit=True)
mat_yellow = simple_mat("TextGelb", srgb(1.0, 0.82, 0.25), emit=True)
mat_outline = simple_mat("TextRand", srgb(0.16, 0.10, 0.04), emit=True)

# Holzbrett
mat_wood = bpy.data.materials.get("Holz") or bpy.data.materials.new("Holz")
wb = NB(mat_wood)
tcb = wb.new('ShaderNodeTexCoord')
mpb = wb.new('ShaderNodeMapping'); mpb.inputs['Scale'].default_value = (6.0, 0.35, 1.0)
wb.link(tcb.outputs['Object'], mpb.inputs['Vector'])
wave = wb.new('ShaderNodeTexNoise'); wb.link(mpb.outputs['Vector'], wave.inputs['Vector'])
wave.inputs['Scale'].default_value = 1.2; wave.inputs['Detail'].default_value = 6; wave.inputs['Roughness'].default_value = 0.6
wr = wb.new('ShaderNodeValToRGB'); wb.link(wave.outputs['Fac'], wr.inputs[0])
wr.color_ramp.elements[0].position = 0.35; wr.color_ramp.elements[1].position = 0.65
wr.color_ramp.elements[0].color = srgb(0.72, 0.52, 0.32); wr.color_ramp.elements[1].color = srgb(0.86, 0.67, 0.45)
wb.link(wr.outputs['Color'], wb.bsdf.inputs['Base Color']); wb.bsdf.inputs['Roughness'].default_value = 0.55

# Fliesenwand (hell, anders als das dunkle Original)
mat_wall = bpy.data.materials.get("Fliesen") or bpy.data.materials.new("Fliesen")
fb = NB(mat_wall)
br = fb.new('ShaderNodeTexBrick', offset=0.0, squash=1.0)
br.inputs['Scale'].default_value = 0.2; br.inputs['Mortar Size'].default_value = 0.03
br.inputs['Color1'].default_value = srgb(0.93, 0.89, 0.82); br.inputs['Color2'].default_value = srgb(0.89, 0.85, 0.78)
br.inputs['Mortar'].default_value = srgb(0.80, 0.74, 0.65); br.inputs['Row Height'].default_value = 0.5; br.inputs['Brick Width'].default_value = 0.5
tcw = fb.new('ShaderNodeTexCoord')
mpw = fb.new('ShaderNodeMapping'); mpw.inputs['Rotation'].default_value = (math.pi / 2, 0, 0)
fb.link(tcw.outputs['Object'], mpw.inputs['Vector']); fb.link(mpw.outputs['Vector'], br.inputs['Vector'])
fb.link(br.outputs['Color'], fb.bsdf.inputs['Base Color']); fb.bsdf.inputs['Roughness'].default_value = 0.3


def add_obj(name, mesh, mats):
    o = bpy.data.objects.new(name, mesh)
    sc.collection.objects.link(o)
    for mt in mats:
        o.data.materials.append(mt)
    return o


def box(name, size, loc, mats, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = add_obj(name, me, mats); o.location = loc; o.rotation_euler = rot
    return o


# ---------------- Umgebung ----------------
box("Brett", (15, 17, 0.7), V(0.3, -0.35, 0.4), [mat_wood], rot=(0, 0, 0.12))
box("Arbeitsplatte", (60, 40, 0.1), (0, 0, -0.75), [mat_counter])
box("Wand", (60, 0.2, 30), V(0, 10, -10.1), [mat_wall])

world = sc.world or bpy.data.worlds.new("Welt"); sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs['Color'].default_value = srgb(0.95, 0.92, 0.86); bg.inputs['Strength'].default_value = 0.55

sun_d = bpy.data.lights.new("Sonne", 'SUN'); sun_d.energy = 3.2; sun_d.angle = math.radians(3)
sun = bpy.data.objects.new("Sonne", sun_d); sc.collection.objects.link(sun)
sun.location = V(6, 16, 7)
trk = bpy.data.objects.new("Ziel", None); sc.collection.objects.link(trk); trk.location = (0, 0, 0)
cn = sun.constraints.new('TRACK_TO'); cn.target = trk; cn.track_axis = 'TRACK_NEGATIVE_Z'; cn.up_axis = 'UP_Y'

cam_d = bpy.data.cameras.new("Kamera"); cam_d.sensor_fit = 'VERTICAL'; cam_d.angle_y = math.radians(52)
cam = bpy.data.objects.new("Kamera", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = V(0, 12.5, 15.5)
look = bpy.data.objects.new("Blickziel", None); sc.collection.objects.link(look); look.location = V(0, 2.2, -1.2)
cn = cam.constraints.new('TRACK_TO'); cn.target = look; cn.track_axis = 'TRACK_NEGATIVE_Z'; cn.up_axis = 'UP_Y'

# ---------------- Kartoffel-Mesh (+ Formschlüssel "Haufen") ----------------
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=200, v_segments=150, radius=1.0)
co = np.array([v.co[:] for v in bm.verts])
dx, dy, dz = co[:, 0], co[:, 2], -co[:, 1]            # Blender -> three
r = potato_radius(dx, dy, dz)
px, py, pz = dx * r, np.maximum(CY + dy * r, 0.02), dz * r
for v, a, b_, c_ in zip(bm.verts, px, py, pz):
    v.co = V(a, b_, c_)
me = bpy.data.meshes.new("Kartoffel"); bm.to_mesh(me); bm.free()
potato = add_obj("Kartoffel", me, [mat_potato])
for poly in me.polygons:
    poly.use_smooth = True
potato.shape_key_add(name="Basis")
sk = potato.shape_key_add(name="Haufen")
qx, qy, qz = pile_map(px, py, pz, 1.0)
qy = np.maximum(qy, 0.01)
sk.data.foreach_set("co", np.stack([qx, -qz, qy], 1).ravel().astype(np.float32))

# ---------------- Messer ----------------
def knife_mesh(with_handle):
    bm = bmesh.new()
    pts = [(0, 0)]
    for i in range(0, 11): pts.append((6.4 * i / 10, 0))
    def quad(p0, p1, p2, n=10):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)[1:]]
    pts += quad((6.4, 0), (7.6, 0.2), (8.0, 1.0)) + quad((8.0, 1.0), (6.8, 1.55), (5.4, 1.75)) + [(0, 1.9)]
    pts = pts[1:]
    vs = [bm.verts.new(V(x, y, -0.025)) for x, y in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=V(0, 0, 0.05), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Klinge"); bm.to_mesh(me); bm.free()
    return me


def make_knife(name, ghost):
    o = add_obj(name, knife_mesh(not ghost), [mat_ghost if ghost else mat_steel])
    if not ghost:
        h = box(name + "_Griff", (3.4, 0.42, 0.75), V(-1.7, 1.35, 0), [mat_handle]); h.parent = o
        for hx in (-0.8, -1.9, -3.0):
            rv = box(name + "_Niete", (0.16, 0.46, 0.16), V(hx, 1.35, 0), [mat_rivet]); rv.parent = o
    else:
        o.visible_shadow = False
    return o


knife = make_knife("Messer", False)
ghosts = [make_knife(f"Geistklinge{i}", True) for i in range(24)]


def place_knife(k, d, pos, y, blend):
    k.rotation_euler = (0, 0, lerp(math.pi / 2, math.pi, blend))
    k.location = V(pos, y, -3.9) if d == 'x' else V(4.6, y, pos)


def set_hidden(o, h):
    o.hide_render = h; o.hide_viewport = h
    for ch in o.children:
        ch.hide_render = h; ch.hide_viewport = h


# ---------------- Stufen vorberechnen ----------------
def make_cube_object(st, cells_three, masks):
    n = len(cells_three)
    me = bpy.data.meshes.new(f"Wuerfel{st['N']}")
    me.vertices.add(n)
    me.vertices.foreach_set("co", np.stack([cells_three[:, 0], -cells_three[:, 2], cells_three[:, 1]], 1).ravel().astype(np.float32))
    for name, typ in (("rot", 'FLOAT_VECTOR'), ("mask", 'FLOAT'), ("shade", 'FLOAT')):
        me.attributes.new(name, typ, 'POINT')
    me.attributes["mask"].data.foreach_set("value", masks.astype(np.float32))
    me.attributes["shade"].data.foreach_set("value", (0.88 + rng.random(n) * 0.2).astype(np.float32))
    o = add_obj(f"Wuerfel{st['N']}", me, [])
    ng = bpy.data.node_groups.new(f"Wuerfel{st['N']}", 'GeometryNodeTree')
    ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = ng.nodes.new('NodeGroupInput'); go = ng.nodes.new('NodeGroupOutput')
    cube = ng.nodes.new('GeometryNodeMeshCube')
    cube.inputs['Size'].default_value = (st['sx'] * 0.95, st['sz'] * 0.95, st['sy'] * 0.95)
    sm = ng.nodes.new('GeometryNodeSetMaterial'); sm.inputs['Material'].default_value = mat_cube
    iop = ng.nodes.new('GeometryNodeInstanceOnPoints')
    rot = ng.nodes.new('GeometryNodeInputNamedAttribute'); rot.data_type = 'FLOAT_VECTOR'; rot.inputs['Name'].default_value = "rot"
    # jede Würfelfläche merkt sich ihre Richtung als Bit (wie die Schalen-Maske)
    nrm = ng.nodes.new('GeometryNodeInputNormal')
    sxyz = ng.nodes.new('ShaderNodeSeparateXYZ'); ng.links.new(nrm.outputs[0], sxyz.inputs[0])
    total = None
    for comp, op, bitv in (('X', 'GREATER_THAN', 1), ('X', 'LESS_THAN', 2), ('Z', 'GREATER_THAN', 4),
                           ('Z', 'LESS_THAN', 8), ('Y', 'LESS_THAN', 16), ('Y', 'GREATER_THAN', 32)):
        cmp_ = ng.nodes.new('ShaderNodeMath'); cmp_.operation = op
        ng.links.new(sxyz.outputs[comp], cmp_.inputs[0]); cmp_.inputs[1].default_value = 0.5 if op == 'GREATER_THAN' else -0.5
        mul = ng.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
        ng.links.new(cmp_.outputs[0], mul.inputs[0]); mul.inputs[1].default_value = bitv
        if total is None:
            total = mul.outputs[0]
        else:
            add = ng.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
            ng.links.new(total, add.inputs[0]); ng.links.new(mul.outputs[0], add.inputs[1]); total = add.outputs[0]
    store = ng.nodes.new('GeometryNodeStoreNamedAttribute'); store.data_type = 'FLOAT'; store.domain = 'FACE'
    store.inputs['Name'].default_value = "facebit"
    ng.links.new(cube.outputs['Mesh'], store.inputs['Geometry'])
    ng.links.new(total, [i for i in store.inputs if i.name == 'Value' and i.enabled][0])
    ng.links.new(store.outputs['Geometry'], sm.inputs['Geometry'])
    ng.links.new(gi.outputs[0], iop.inputs['Points'])
    ng.links.new(sm.outputs['Geometry'], iop.inputs['Instance'])
    ng.links.new(rot.outputs['Attribute'], iop.inputs['Rotation'])
    ng.links.new(iop.outputs['Instances'], go.inputs[0])
    mod = o.modifiers.new("Wuerfel", 'NODES'); mod.node_group = ng
    return o


for st in STAGES:
    nx = nz = st['N'] // 2
    sx, sz = 2 * A / (nx + 1), 2 * C / (nz + 1)
    sy = (sx + sz) / 2
    ny = math.ceil((CY + B * 1.12) / sy)
    st.update(nx=nx, nz=nz, sx=sx, sz=sz, sy=sy, K=nx // st['P'])
    if st['N'] <= 100:
        I, J, L = np.meshgrid(np.arange(-1, nx + 2), np.arange(-1, nz + 2), np.arange(-1, ny + 1), indexing='ij')
        ins = inside_potato(-A + (I + 0.5) * sx, (L + 0.5) * sy, -C + (J + 0.5) * sz)
        ins[:, :, 0] = False
        core = ins[1:-1, 1:-1, 1:-1]
        m = np.zeros(core.shape, int)
        m |= (~ins[2:, 1:-1, 1:-1]) * 1; m |= (~ins[:-2, 1:-1, 1:-1]) * 2
        m |= (~ins[1:-1, 1:-1, 2:]) * 4
        m |= ((~ins[1:-1, 1:-1, :-2]) & (L[1:-1, 1:-1, 1:-1] > 0)) * 8
        m |= (~ins[1:-1, 2:, 1:-1]) * 16; m |= (~ins[1:-1, :-2, 1:-1]) * 32
        ii, jj, ll = np.nonzero(core)
        cells = np.stack([-A + (ii + 0.5) * sx, (ll + 0.5) * sy, -C + (jj + 0.5) * sz], 1)
        st['total'] = len(cells)
        c = {10: 0.22, 50: 0.6, 100: 0.85}[st['N']]
        ex, ey, ez = pile_map(cells[:, 0], cells[:, 1], cells[:, 2], c)
        j = c * 0.35
        n = len(cells)
        st['s'] = cells
        st['e'] = np.stack([ex + (rng.random(n) - 0.5) * sx * j, np.maximum(ey, sy * 0.47), ez + (rng.random(n) - 0.5) * sz * j], 1)
        st['delay'] = cells[:, 1] / (CY + B) * 0.25 + rng.random(n) * 0.12
        if c >= 0.5:
            st['rot'] = np.stack([np.floor(rng.random(n) * 4) * math.pi / 2 + (rng.random(n) - 0.5) * 0.5,
                                  (rng.random(n) - 0.5) * 0.8,
                                  np.floor(rng.random(n) * 4) * math.pi / 2 + (rng.random(n) - 0.5) * 0.5], 1)
        else:
            st['rot'] = (rng.random((n, 3)) - 0.5) * c * 1.2
        mask = m[ii, jj, ll]
        if st['N'] >= 50:  # im Haufen soll – wie im Original – das gelbe Innere dominieren
            mask = np.where(rng.random(n) < 0.3, mask, 0)
        st['obj'] = make_cube_object(st, cells, mask)
    else:
        M = 400000
        p = rng.random((M, 3))
        hit = inside_potato((p[:, 0] * 2 - 1) * A * 1.1, p[:, 1] * (CY + B * 1.12), (p[:, 2] * 2 - 1) * C * 1.1).mean()
        vol = hit * (2 * A * 1.1) * (CY + B * 1.12) * (2 * C * 1.1)
        st['total'] = int(round(vol / (sx * sy * sz) / 1000) * 1000)

t0 = 0.0
for st in STAGES:
    st['start'] = t0
    st['cutStart'] = t0 + INTRO
    st['zStart'] = st['cutStart'] + st['P'] * st['pass_'] + SWITCH
    st['cutEnd'] = st['zStart'] + st['P'] * st['pass_']
    st['end'] = st['cutEnd'] + COLLAPSE + HOLD
    t0 = st['end']
DURATION = t0

# ---------------- Zähler (Text an der Kamera) ----------------
FONT = None
for f in [r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\seguibl.ttf", "/System/Library/Fonts/Supplemental/Arial Black.ttf",
          "/Library/Fonts/Arial Black.ttf", "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"]:
    if os.path.exists(f):
        FONT = bpy.data.fonts.load(f, check_existing=True); break
HALF = 10 * math.tan(math.radians(26))


def ndc_y(px_y): return (1 - 2 * px_y / RES[1]) * HALF


def text(name, body, size, px_y, mat, z, offset=0.0):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size
    cu.align_x = 'CENTER'; cu.align_y = 'BOTTOM_BASELINE'; cu.offset = offset
    if FONT: cu.font = FONT
    o = add_obj(name, cu, [mat]); o.parent = cam; o.location = (0, ndc_y(px_y), z)
    o.visible_shadow = False
    return o


EM_NUM = 150 / RES[1] * 2 * HALF
EM_LAB = 64 / RES[1] * 2 * HALF
counters = {}
for key, y, label in (("cuts", 300, "SCHNITTE"), ("cubes", 1660, "WÜRFEL")):
    counters[key] = (text(key, "0", EM_NUM, y, mat_white, -10), text(key + "_rand", "0", EM_NUM, y, mat_outline, -10.01, 0.035))
    text(key + "_label", label, EM_LAB, y + 82, mat_yellow, -10)
    text(key + "_label_rand", label, EM_LAB, y + 82, mat_outline, -10.01, 0.025)


def set_counter(key, s):
    width = 0.66 * len(s) * EM_NUM
    k = min(1.0, (900 / RES[0] * 2 * HALF * RES[0] / RES[1]) / width)
    for o in counters[key]:
        o.data.body = s; o.scale = (k, k, k)


def fmt(n): return f"{n:,}".replace(",", ".")


# ---------------- Bild für Bild ----------------
def nodeval(name, v):
    mat_potato.node_tree.nodes[name].outputs[0].default_value = v


def set_time(t):
    st = next((s for s in STAGES if t < s['end']), STAGES[-1])
    for s in STAGES:
        if 'obj' in s: set_hidden(s['obj'], True)
    for g in ghosts: set_hidden(g, True)
    for k, v in (("uSx", st['sx']), ("uSz", st['sz']), ("uNx", st['nx']), ("uNz", st['nz']), ("uP", st['P']),
                 ("uCellX", st['sx']), ("uCellY", st['sy']), ("uCellZ", st['sz'])):
        nodeval(k, v)
    for ax, s_ in (("X", st['sx']), ("Z", st['sz'])):
        w = min(0.03, s_ * 0.18)
        nodeval("uW" + ax.lower(), w); nodeval("uCov" + ax, clamp(2 * w / s_, 0, 1)); nodeval("uDense" + ax, smoothstep(0.08, 0.3, PX / s_))
    nodeval("uPile", 0.0)
    potato.data.shape_keys.key_blocks["Haufen"].value = 0.0
    set_hidden(potato, False)
    potato.location = (0, 0, 0)
    if t < st['cutStart']:
        u = clamp((t - st['start']) / (INTRO * 0.85), 0, 1)
        potato.location = (0, 0, (1 - ease_in(u)) * 2.2)

    sw0 = st['zStart'] - SWITCH
    if t < st['zStart']:
        d, jf, blend = 'x', (t - st['cutStart']) / st['pass_'], 0.0
    else:
        d, jf, blend = 'z', (t - st['zStart']) / st['pass_'], 1.0
    if sw0 <= t < st['zStart']:
        blend = ease_out((t - sw0) / SWITCH)
    passX = 0 if t < st['cutStart'] else clamp(math.floor((t - st['cutStart']) / st['pass_'] + 0.45), 0, st['P'])
    passZ = 0 if t < st['zStart'] else clamp(math.floor((t - st['zStart']) / st['pass_'] + 0.45), 0, st['P'])
    cuts = (passX + passZ) * st['K']
    cubes = round(st['total'] * passZ / st['P'])
    if st['N'] >= 250: cubes = round(cubes / 1000) * 1000

    ky, j = KNIFE_TOP, 0
    in_cut = st['cutStart'] <= t < st['cutEnd'] and not (sw0 <= t < st['zStart'])
    if in_cut:
        j = math.floor(jf); f = jf - j
        ky = KNIFE_TOP if f < 0.25 else (lerp(KNIFE_TOP, 0.02, ease_in((f - 0.25) / 0.3)) if f < 0.55
                                         else lerp(0.02, KNIFE_TOP, ease_out((f - 0.55) / 0.45)))
    elif sw0 <= t < st['zStart']:
        j, d = 0, 'z'
    elif t < st['cutStart']:
        j = 0
    else:
        j = st['P'] - 1; ky = lerp(KNIFE_TOP, KNIFE_TOP + 6, clamp((t - st['cutEnd']) / 0.5, 0, 1))
    if t < st['cutStart']: d = 'x'
    s_, ext = (st['sx'], A) if d == 'x' else (st['sz'], C)
    line_pos = lambda m: -ext + (j + 1 + m * st['P']) * s_
    place_knife(knife, d, line_pos(0), ky, blend)
    kv = st['start'] + INTRO * 0.5 <= t < st['cutEnd'] + 0.5
    set_hidden(knife, not kv)
    if kv and st['K'] > 1:
        ng_ = min(st['K'], 25)
        for m in range(1, ng_):
            g = ghosts[m - 1]; set_hidden(g, False)
            place_knife(g, d, line_pos(round(m * (st['K'] - 1) / min(st['K'] - 1, 24))), ky, blend)
    nodeval("uPassX", passX); nodeval("uPassZ", passZ)

    if t >= st['cutEnd']:
        cuts, cubes = st['N'], st['total']
        u = clamp((t - st['cutEnd']) / COLLAPSE, 0, 1)
        if 'obj' in st:
            set_hidden(potato, True); set_hidden(st['obj'], False)
            v = np.clip((u - st['delay'] * 0.6) / 0.75, 0, 1)
            c1, c3 = 1.4, 2.4
            e = np.where(v < 1, 1 + c3 * (v - 1) ** 3 + c1 * (v - 1) ** 2, 1)
            ey = np.minimum(1, v * 1.15) ** 2
            s, en = st['s'], st['e']
            pos = np.stack([s[:, 0] + (en[:, 0] - s[:, 0]) * e, s[:, 1] + (en[:, 1] - s[:, 1]) * ey, s[:, 2] + (en[:, 2] - s[:, 2]) * e], 1)
            rot = st['rot'] * v[:, None]
            me = st['obj'].data
            me.vertices.foreach_set("co", np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], 1).ravel().astype(np.float32))
            me.attributes["rot"].data.foreach_set("vector", np.stack([rot[:, 0], -rot[:, 2], rot[:, 1]], 1).ravel().astype(np.float32))
            me.update()
        else:
            nodeval("uPile", clamp(u * 3, 0, 1))
            potato.data.shape_keys.key_blocks["Haufen"].value = ease_out(u)
    set_counter("cuts", fmt(cuts))
    set_counter("cubes", ("≈ " if st['N'] >= 250 and cubes > 0 else "") + fmt(cubes))


def kartoffel_frame(scene, *args):
    set_time((scene.frame_current - 1) / FPS)


bpy.app.handlers.frame_change_pre.append(kartoffel_frame)

# ---------------- Render-Einstellungen ----------------
r_ = sc.render
r_.resolution_x, r_.resolution_y, r_.resolution_percentage = RES[0], RES[1], 100
r_.fps = FPS
sc.frame_start, sc.frame_end = 1, math.ceil(DURATION * FPS)
r_.use_lock_interface = True
sc.view_settings.view_transform = 'Standard'
if ENGINE == "CYCLES":
    r_.engine = 'CYCLES'
    sc.cycles.samples = 64; sc.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dev in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
            try:
                prefs.compute_device_type = dev; prefs.get_devices()
                if any(d.type == dev for d in prefs.devices):
                    for d_ in prefs.devices: d_.use = True
                    sc.cycles.device = 'GPU'; break
            except Exception: pass
    except Exception: pass
else:
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: r_.engine = eng; break
        except Exception: pass
    try: sc.eevee.taa_render_samples = 64
    except Exception: pass

try: r_.image_settings.media_type = 'VIDEO'
except Exception: pass
r_.image_settings.file_format = 'FFMPEG'
r_.ffmpeg.format = 'MPEG4'
r_.ffmpeg.codec = 'H264'
r_.ffmpeg.constant_rate_factor = 'HIGH'
r_.ffmpeg.audio_codec = 'AAC'
r_.ffmpeg.audio_bitrate = 192
r_.filepath = os.path.join(ORDNER, VIDEO)

snd = os.path.join(ORDNER, SOUND)
if os.path.exists(snd):
    se = sc.sequence_editor_create()
    coll = getattr(se, "strips", None) or getattr(se, "sequences")
    for s in list(coll): coll.remove(s)
    coll.new_sound("Sound", snd, 1, 1)
else:
    print(f"ACHTUNG: {snd} nicht gefunden – Video wird ohne Ton gerendert.")

sc.frame_set(1)
print(f"Fertig aufgebaut: {sc.frame_end} Bilder ({DURATION:.1f} s). Jetzt Rendern -> Animation rendern (Strg+F12).")
