"""Build the Shrek player body on the arctic CS 1.6 skeleton.

Run inside Blender with the arctic armature already imported.

Everything is authored in the imported T-pose and rigid-weighted: each vertex
belongs to exactly one GoldSrc bone with weight 1.0.  The geometry is kept
under the MDL v10 limit of 2048 vertices for the single "body" mesh.
"""
from __future__ import annotations

import math
import os

import bpy
from mathutils import Euler, Matrix, Vector

ROOT = r"C:\AI\goldsrc\shrek_player"
ARM_NAME = "arctic_ARM"
MESH_NAME = "shrek_body"
COLLECTION_NAME = "Shrek"
CX = 0.234  # the arctic skeleton's centre line
W = H = 512

# Same layout as make_texture.py (top-left pixel coordinates).
PATCHES = {
    "skin": (0, 0, 128, 128),
    "tunic": (128, 0, 128, 128),
    "vest": (256, 0, 128, 128),
    "pants": (384, 0, 128, 128),
    "shoe": (0, 128, 128, 128),
    "sole": (128, 128, 128, 128),
    "belt": (256, 128, 128, 128),
    "ear_inner": (384, 128, 128, 128),
    "nose": (0, 256, 128, 128),
    "eye_white": (128, 256, 64, 64),
    "iris": (192, 256, 64, 64),
    "pupil": (256, 256, 64, 64),
    "brow": (320, 256, 64, 64),
    "mouth": (384, 256, 64, 64),
    "teeth": (448, 256, 64, 64),
    "tongue": (0, 384, 64, 64),
    "buckle": (64, 384, 64, 64),
    "cheek": (128, 384, 64, 64),
    "dark": (192, 384, 64, 64),
    "highlight": (256, 384, 64, 64),
    "unused": (320, 384, 64, 64),
}


def _rect(name: str):
    x, y, w, h = PATCHES[name]
    return (x / W, 1.0 - (y + h) / H, (x + w) / W, 1.0 - y / H)


def uv_center(name: str):
    u0, v0, u1, v1 = _rect(name)
    return ((u0 + u1) * 0.5, (v0 + v1) * 0.5)


def uv_map(name: str, u: float, v: float):
    u0, v0, u1, v1 = _rect(name)
    return (u0 + u * (u1 - u0), v0 + v * (v1 - v0))


class Builder:
    def __init__(self):
        self.verts: list[Vector] = []
        self.bones: list[str] = []
        self.faces: list[tuple[int, ...]] = []
        self.face_uvs: list[list[tuple[float, float]]] = []
        self.face_smooth: list[bool] = []

    def vert(self, co, bone: str) -> int:
        self.verts.append(Vector(co))
        self.bones.append(bone)
        return len(self.verts) - 1

    def face(self, ids, uvs, smooth=True):
        assert len(ids) == len(uvs), (len(ids), len(uvs))
        self.faces.append(tuple(ids))
        self.face_uvs.append(list(uvs))
        self.face_smooth.append(bool(smooth))

    # ------------------------------------------------------------------ primitives
    def loft(self, rings, sides, bones, region, closed=True, cap_start=False,
             cap_end=False, opening=None, smooth=True):
        """Vertical loft.

        rings:   [(z, cx, cy, rx, ry), ...] bottom to top.
        bones:   one bone name or one name per ring.
        opening: for open strips, one half-opening angle in degrees per ring,
                 measured from the front (-Y) centre line.
        """
        n = len(rings)
        if isinstance(bones, str):
            bones = [bones] * n
        cols = sides if closed else sides + 1
        start = len(self.verts)
        for i, (z, cx, cy, rx, ry) in enumerate(rings):
            if closed:
                angles = [2 * math.pi * j / sides for j in range(sides)]
            else:
                half = math.radians(opening[i])
                angles = [half + (2 * math.pi - 2 * half) * j / sides
                          for j in range(cols)]
            for a in angles:
                self.vert((cx + rx * math.sin(a), cy - ry * math.cos(a), z),
                          bones[i])
        for i in range(n - 1):
            for j in range(sides):
                j2 = (j + 1) % cols if closed else j + 1
                a = start + i * cols + j
                b = start + i * cols + j2
                c = start + (i + 1) * cols + j2
                d = start + (i + 1) * cols + j
                v0, v1 = i / (n - 1), (i + 1) / (n - 1)
                u0 = j / sides
                u1 = (j + 1) / sides
                self.face((a, b, c, d), [
                    uv_map(region, u0, v0), uv_map(region, u1, v0),
                    uv_map(region, u1, v1), uv_map(region, u0, v1),
                ], smooth)
        if cap_start:
            ci = self.vert((rings[0][1], rings[0][2], rings[0][0]), bones[0])
            for j in range(sides):
                j2 = (j + 1) % sides
                self.face((ci, start + j2, start + j),
                          [uv_center(region)] * 3, False)
        if cap_end:
            ci = self.vert((rings[-1][1], rings[-1][2], rings[-1][0]), bones[-1])
            base = start + (n - 1) * cols
            for j in range(sides):
                j2 = (j + 1) % sides
                self.face((ci, base + j, base + j2),
                          [uv_center(region)] * 3, False)

    def tube(self, points, rx, ry, sides, bone, region, caps=(True, True),
             smooth=True):
        pts = [Vector(p) for p in points]
        n = len(pts)
        if not isinstance(rx, (list, tuple)):
            rx = [rx] * n
        if not isinstance(ry, (list, tuple)):
            ry = [ry] * n
        start = len(self.verts)
        for i, p in enumerate(pts):
            tangent = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
            if tangent.length < 1e-9:
                tangent = Vector((0, 0, 1))
            tangent.normalize()
            up = Vector((0, 0, 1)) if abs(tangent.z) < 0.92 else Vector((0, 1, 0))
            right = up.cross(tangent).normalized()
            up2 = tangent.cross(right).normalized()
            for j in range(sides):
                th = 2 * math.pi * j / sides
                co = p + right * (math.cos(th) * rx[i]) + up2 * (math.sin(th) * ry[i])
                self.vert(co, bone)
        for i in range(n - 1):
            for j in range(sides):
                a = start + i * sides + j
                b = start + i * sides + (j + 1) % sides
                c = start + (i + 1) * sides + (j + 1) % sides
                d = start + (i + 1) * sides + j
                v0, v1 = i / (n - 1), (i + 1) / (n - 1)
                self.face((a, b, c, d), [
                    uv_map(region, j / sides, v0), uv_map(region, (j + 1) / sides, v0),
                    uv_map(region, (j + 1) / sides, v1), uv_map(region, j / sides, v1),
                ], smooth)
        if caps[0]:
            ci = self.vert(pts[0], bone)
            for j in range(sides):
                a = start + (j + 1) % sides
                b = start + j
                self.face((ci, a, b), [uv_center(region)] * 3, False)
        if caps[1]:
            ci = self.vert(pts[-1], bone)
            base = start + (n - 1) * sides
            for j in range(sides):
                self.face((ci, base + j, base + (j + 1) % sides),
                          [uv_center(region)] * 3, False)

    def ellipsoid(self, center, radii, seg, rings, bone, region, smooth=True):
        c = Vector(center)
        rx, ry, rz = radii
        top = self.vert(c + Vector((0, 0, rz)), bone)
        start = len(self.verts)
        for j in range(1, rings):
            phi = math.pi * j / rings
            sp, cp = math.sin(phi), math.cos(phi)
            for i in range(seg):
                th = 2 * math.pi * i / seg
                co = c + Vector((rx * sp * math.cos(th), ry * sp * math.sin(th), rz * cp))
                self.vert(co, bone)
        bottom = self.vert(c + Vector((0, 0, -rz)), bone)
        for i in range(seg):
            a = start + i
            b = start + (i + 1) % seg
            self.face((top, a, b), [
                uv_map(region, 0.5, 1.0),
                uv_map(region, i / seg, 1.0 - 1.0 / rings),
                uv_map(region, (i + 1) / seg, 1.0 - 1.0 / rings),
            ], smooth)
        for j in range(1, rings - 1):
            row0 = start + (j - 1) * seg
            row1 = start + j * seg
            v0 = 1.0 - j / rings
            v1 = 1.0 - (j + 1) / rings
            for i in range(seg):
                i2 = (i + 1) % seg
                self.face((row0 + i, row1 + i, row1 + i2, row0 + i2), [
                    uv_map(region, i / seg, v0), uv_map(region, i / seg, v1),
                    uv_map(region, (i + 1) / seg, v1), uv_map(region, (i + 1) / seg, v0),
                ], smooth)
        last = start + (rings - 2) * seg
        for i in range(seg):
            a = last + (i + 1) % seg
            b = last + i
            self.face((bottom, a, b), [
                uv_map(region, 0.5, 0.0),
                uv_map(region, (i + 1) / seg, 1.0 / rings),
                uv_map(region, i / seg, 1.0 / rings),
            ], smooth)

    def box(self, center, size, bone, region, rot=None, smooth=False):
        c = Vector(center)
        hx, hy, hz = (v * 0.5 for v in size)
        local = [
            (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
            (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
        ]
        m = Euler(rot).to_matrix() if rot else Matrix.Identity(3)
        ids = [self.vert(c + m @ Vector(p), bone) for p in local]
        faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                 (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
        uv = uv_center(region)
        for f in faces:
            self.face(tuple(ids[i] for i in f), [uv] * 4, smooth)

    def disk(self, center, normal, radius, sides, bone, region, smooth=False):
        c = Vector(center)
        n = Vector(normal).normalized()
        up = Vector((0, 0, 1)) if abs(n.z) < 0.92 else Vector((0, 1, 0))
        right = up.cross(n).normalized()
        up2 = n.cross(right).normalized()
        ci = self.vert(c, bone)
        start = len(self.verts)
        for j in range(sides):
            th = 2 * math.pi * j / sides
            self.vert(c + right * (math.cos(th) * radius) + up2 * (math.sin(th) * radius), bone)
        uv = uv_center(region)
        for j in range(sides):
            self.face((ci, start + j, start + (j + 1) % sides), [uv] * 3, smooth)


# ---------------------------------------------------------------------- helpers
JAW_C = (CX, -2.8, 61.0)
JAW_R = (5.7, 3.9, 3.1)


def jaw_y(x, z):
    """Front surface of the jaw ellipsoid, used to lay the mouth on the face."""
    cx, cy, cz = JAW_C
    rx, ry, rz = JAW_R
    t = 1.0 - ((x - cx) / rx) ** 2 - ((z - cz) / rz) ** 2
    t = max(0.04, t)
    return cy - ry * math.sqrt(t)


def leg_z(a, b, z):
    """Point on the hip->knee (or knee->ankle) line at height z."""
    t = (a[2] - z) / (a[2] - b[2])
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, z)


def build_mesh():
    b = Builder()

    # ------------------------------------------------------------------ pelvis
    b.loft([(32.8, CX, -0.2, 7.8, 6.5),
            (34.6, CX, -0.2, 9.2, 7.4),
            (37.0, CX, -0.3, 9.8, 7.8),
            (39.8, CX, -0.5, 9.9, 7.9)],
           12, "Bip01 Pelvis", "pants", cap_start=True, cap_end=True)

    # ------------------------------------------------------------------ torso / tunic
    torso_rings = [
        (39.2, CX, -0.6, 9.9, 8.0),   # Spine
        (42.2, CX, -0.8, 10.5, 8.6),  # Spine1
        (45.4, CX, -0.9, 10.8, 8.7),  # Spine2
        (48.6, CX, -0.8, 10.7, 8.4),  # Spine2
        (51.8, CX, -0.6, 10.3, 7.9),  # Spine3
        (54.4, CX, -0.3, 9.6, 7.2),   # Spine3
        (56.4, CX,  0.1, 8.2, 6.4),   # Spine3
    ]
    torso_bones = ["Bip01 Spine", "Bip01 Spine1", "Bip01 Spine2",
                   "Bip01 Spine2", "Bip01 Spine3", "Bip01 Spine3",
                   "Bip01 Spine3"]
    b.loft(torso_rings, 12, torso_bones, "tunic", cap_start=True, cap_end=True)

    # open leather vest: one surface, stitch lines land on the open edges
    def torso_at(z):
        for i in range(len(torso_rings) - 1):
            z0, _, cy0, rx0, ry0 = torso_rings[i]
            z1, _, cy1, rx1, ry1 = torso_rings[i + 1]
            if z0 <= z <= z1:
                t = (z - z0) / (z1 - z0)
                return (cy0 + (cy1 - cy0) * t, rx0 + (rx1 - rx0) * t,
                        ry0 + (ry1 - ry0) * t)
        z0, _, cy0, rx0, ry0 = torso_rings[-1]
        return (cy0, rx0, ry0)

    vest_z = [41.2, 44.2, 47.2, 50.2, 53.2, 55.2, 56.3]
    vest_rings = []
    for z in vest_z:
        cy, rx, ry = torso_at(z)
        vest_rings.append((z, CX, cy - 0.05, rx + 0.75, ry + 0.75))
    vest_bones = ["Bip01 Spine1", "Bip01 Spine2", "Bip01 Spine2",
                  "Bip01 Spine3", "Bip01 Spine3", "Bip01 Spine3",
                  "Bip01 Spine3"]
    opening = [16, 16, 18, 20, 24, 30, 38]
    b.loft(vest_rings, 10, vest_bones, "vest", closed=False, opening=opening)

    # belt and buckle
    b.loft([(39.4, CX, -0.6, 10.35, 8.4),
            (40.2, CX, -0.65, 10.45, 8.5),
            (41.2, CX, -0.65, 10.3, 8.35)],
           12, "Bip01 Spine", "belt", cap_start=False, cap_end=False)
    b.box((CX, -8.95, 40.3), (3.2, 0.7, 2.2), "Bip01 Spine", "buckle")
    b.box((CX, -9.3, 40.3), (1.6, 0.3, 1.1), "Bip01 Spine", "dark")

    # thick neck + collar
    b.tube([(CX, -0.5, 54.4), (CX, -0.5, 57.2), (CX, -0.4, 60.2)],
           [4.0, 3.85, 3.55], [3.9, 3.75, 3.45], 8,
           "-- Neck smooth", "skin", caps=(True, True))
    b.loft([(55.8, CX, 0.0, 4.6, 4.55),
            (56.6, CX, 0.0, 4.4, 4.35),
            (57.2, CX, 0.0, 4.15, 4.1)],
           8, "Bip01 Spine3", "tunic", cap_start=False, cap_end=False)

    # ------------------------------------------------------------------ legs
    for s in (1, -1):
        hip = (CX + s * (3.853 - CX), 0.025, 36.954)
        knee = (CX + s * (6.154 - CX), -1.388, 20.602)
        ankle = (CX + s * (8.254 - CX), -0.222, 5.665)
        thigh_bone = "Bip01 L Thigh" if s > 0 else "Bip01 R Thigh"
        calf_bone = "Bip01 L Calf" if s > 0 else "Bip01 R Calf"
        foot_bone = "Bip01 L Foot" if s > 0 else "Bip01 R Foot"
        toe_bone = "Bip01 L Toe0" if s > 0 else "Bip01 R Toe0"
        knee_helper = "-- L Knee" if s > 0 else "-- R Knee"
        ankle_helper = "-- L ankle" if s > 0 else "-- R Ankle"

        b.tube([(hip[0], hip[1], hip[2]),
                leg_z(hip, knee, 30.0),
                leg_z(hip, knee, 25.0),
                (knee[0], knee[1], knee[2])],
               [5.05, 4.8, 4.35, 4.1], [4.95, 4.7, 4.25, 4.0],
               8, thigh_bone, "pants", caps=(True, True))
        b.ellipsoid((knee[0], knee[1], knee[2]), (4.12, 4.02, 4.0),
                    8, 4, knee_helper, "pants")
        b.tube([(knee[0], knee[1], knee[2]),
                leg_z(knee, ankle, 15.0),
                leg_z(knee, ankle, 9.5),
                (ankle[0], ankle[1], ankle[2])],
               [4.0, 3.7, 3.3, 3.0], [3.9, 3.6, 3.2, 2.9],
               8, calf_bone, "pants", caps=(True, True))
        b.ellipsoid((ankle[0], ankle[1], 5.5), (2.75, 2.7, 2.65),
                    8, 4, ankle_helper, "pants")
        # trouser cuff hanging over the shoe
        b.tube([(ankle[0], ankle[1], 6.1), (ankle[0], ankle[1], 8.4)],
               [3.55, 3.45], [3.5, 3.4], 8, calf_bone, "pants",
               caps=(False, False))

        # shoe: rear/mid on Foot, toe on Toe0
        b.tube([(ankle[0], 2.0, 2.9), (ankle[0], -0.5, 3.0),
                (ankle[0], -3.5, 2.8)],
               [2.9, 3.15, 3.0], [2.55, 2.75, 2.5],
               8, foot_bone, "shoe", caps=(True, False))
        b.tube([(ankle[0], -3.4, 2.65), (ankle[0], -6.0, 2.2),
                (ankle[0], -8.2, 1.7)],
               [3.05, 2.8, 2.3], [2.6, 2.3, 1.6],
               8, toe_bone, "shoe", caps=(False, True))
        b.box((ankle[0], -0.7, 0.42), (5.3, 5.4, 0.84), foot_bone, "sole")
        b.box((ankle[0], -5.9, 0.38), (4.8, 4.9, 0.76), toe_bone, "sole")

    # ------------------------------------------------------------------ arms
    for s in (1, -1):
        shoulder = (CX + s * (8.336 - CX), -0.696, 54.784)
        elbow = (CX + s * (18.576 - CX), -0.654, 54.558)
        wrist = (CX + s * (29.949 - CX), -0.698, 54.304)
        ua = "Bip01 L UpperArm" if s > 0 else "Bip01 R UpperArm"
        fa = "Bip01 L Forearm" if s > 0 else "Bip01 R Forearm"
        ha = "Bip01 L Hand" if s > 0 else "Bip01 R Hand"
        elbow_helper = "-- L Elbow" if s > 0 else "-- R Elbow"
        wrist_helper = "-- L wrist" if s > 0 else "-- R wrist"
        f0 = "Bip01 L Finger0" if s > 0 else "Bip01 R Finger0"
        f01 = "Bip01 L Finger01" if s > 0 else "Bip01 R Finger01"
        f1 = "Bip01 L Finger1" if s > 0 else "Bip01 R Finger1"
        f11 = "Bip01 L Finger11" if s > 0 else "Bip01 R Finger11"
        x = lambda v: CX + s * (v - CX)

        # rounded shoulder, short cream sleeve + rolled cuff
        b.ellipsoid((x(8.6), -0.7, 54.55), (3.9, 3.55, 3.55),
                    8, 4, ua, "tunic")
        b.tube([(x(8.0), -0.7, 54.78), (x(10.8), -0.7, 54.78),
                (x(13.6), -0.7, 54.76)],
               [3.55, 3.55, 3.45], [3.55, 3.55, 3.45],
               8, ua, "tunic", caps=(True, False))
        b.tube([(x(13.4), -0.7, 54.76), (x(14.0), -0.7, 54.76)],
               [3.75, 3.7], [3.75, 3.7], 8, ua, "tunic",
               caps=(False, False))

        # bare green arm
        b.tube([(x(13.2), -0.7, 54.76), (x(15.2), -0.68, 54.69), elbow],
               [3.2, 3.35, 2.85], [3.2, 3.35, 2.85],
               8, ua, "skin", caps=(True, True))
        b.ellipsoid(elbow, (2.92, 2.9, 2.88), 8, 4, elbow_helper, "skin")
        b.tube([(elbow[0], elbow[1], elbow[2]),
                (x(23.0), -0.67, 54.5),
                (x(27.0), -0.69, 54.4), wrist],
               [2.8, 2.55, 2.2, 2.0], [2.8, 2.55, 2.2, 2.0],
               8, fa, "skin", caps=(True, True))
        b.ellipsoid(wrist, (2.0, 2.0, 2.0), 8, 4, wrist_helper, "skin")

        # broad cartoon palm
        b.tube([(x(29.8), -0.7, 54.3), (x(32.0), -0.7, 54.25),
                (x(34.2), -0.7, 54.2)],
               [2.0, 2.7, 2.8], [1.7, 2.1, 2.0],
               8, ha, "skin", caps=(True, True))

        # thumb, two rigid segments
        b.tube([(x(32.0), -2.3, 54.1), (x(33.4), -3.1, 53.7)],
               [1.0, 0.9], [1.0, 0.9], 4, f0, "skin",
               caps=(True, False))
        b.tube([(x(33.3), -3.05, 53.75), (x(34.7), -3.6, 53.3)],
               [0.88, 0.7], [0.88, 0.7], 4, f01, "skin",
               caps=(False, True))

        # three fingers: first segment on Finger1, tip on Finger11
        for fy in (-1.45, 0.0, 1.45):
            b.tube([(x(34.0), fy, 54.25), (x(35.8), fy, 54.22)],
                   [0.72, 0.66], [0.72, 0.66], 4, f1, "skin",
                   caps=(True, False))
            b.tube([(x(35.7), fy, 54.22), (x(37.2), fy, 54.15)],
                   [0.64, 0.46], [0.64, 0.46], 4, f11, "skin",
                   caps=(False, True))

    # ------------------------------------------------------------------ head
    head_c = (CX, -0.4, 64.9)
    b.ellipsoid(head_c, (7.0, 6.2, 6.9), 12, 7, "Bip01 Head", "skin")
    b.ellipsoid((CX, -2.8, 61.0), (5.7, 3.9, 3.1), 10, 5,
                "Bip01 Head", "skin")
    b.ellipsoid((CX, -5.0, 59.1), (3.2, 1.5, 1.15), 8, 4,
                "Bone01", "skin")
    for sx in (-1, 1):
        b.ellipsoid((CX + sx * 3.8, -5.15, 62.4), (2.05, 1.7, 1.9),
                    8, 4, "Bip01 Head", "skin")
        # trumpet ear: shorter than a Yoda wing, flared and angled forward so
        # the dark opening is visible from the front like Shrek's.
        pts = [(CX + sx * 5.7, 0.1, 65.0),
               (CX + sx * 7.5, -0.5, 65.5),
               (CX + sx * 9.2, -1.3, 66.0),
               (CX + sx * 10.4, -1.9, 66.4)]
        b.tube(pts, [1.1, 1.0, 1.25, 1.55], [1.55, 1.45, 1.95, 2.45],
               8, "Bip01 Head", "skin", caps=(True, False))
        axis = (Vector(pts[-1]) - Vector(pts[-2])).normalized()
        b.disk(Vector(pts[-1]) + axis * 0.04, axis, 2.55, 8,
               "Bip01 Head", "ear_inner")

    # brow ridge and brows: a visible gap above the nose, inner ends slightly
    # raised so the resting face reads as a friendly smirk, not a scowl.
    b.ellipsoid((CX, -5.7, 66.6), (6.2, 1.05, 1.3), 10, 4,
                "Bip01 Head", "skin")
    for sx in (-1, 1):
        brow_pts = [(CX + sx * 1.7, -6.40, 67.05),
                    (CX + sx * 3.3, -6.50, 66.88),
                    (CX + sx * 4.9, -6.35, 66.62)]
        b.tube(brow_pts, [0.42, 0.46, 0.34], [0.42, 0.48, 0.32], 5,
               "Bip01 Head", "brow", caps=(True, True))

    # eyes: shallow sclera with flat iris/pupil discs under a heavy brow
    for sx in (-1, 1):
        ex = CX + sx * 2.85
        b.ellipsoid((ex, -6.0, 65.5), (1.10, 0.48, 1.18),
                    10, 5, "Bip01 Head", "eye_white")
        b.disk((ex, -6.51, 65.5), (0, -1, 0), 0.66, 8,
               "Bip01 Head", "iris")
        b.disk((ex, -6.53, 65.5), (0, -1, 0), 0.33, 6,
               "Bip01 Head", "pupil")
        b.disk((ex - 0.14, -6.55, 65.68), (0, -1, 0), 0.12, 5,
               "Bip01 Head", "highlight")

    # nose: bridge + broad bulb + nostrils
    b.ellipsoid((CX, -6.1, 65.6), (1.4, 1.55, 2.2), 8, 4,
                "Bip01 Head", "skin")
    b.ellipsoid((CX, -7.3, 63.7), (2.85, 3.0, 2.3), 10, 5,
                "Bip01 Head", "nose")
    for sx in (-1, 1):
        b.disk((CX + sx * 1.02, -9.9, 62.65), (0, -1, -0.15), 0.38, 6,
               "Bip01 Head", "dark")

    # wide grin: dark cavity, a strip of teeth, and a soft lower lip
    mouth = []
    for i in range(7):
        x = -4.7 + i * (9.4 / 6)
        z = 61.20 + 1.05 * (abs(x) / 4.7) ** 1.7
        y = jaw_y(CX + x, z) - 0.10
        mouth.append((CX + x, y, z))
    b.tube(mouth, [0.30] * 7, [0.62] * 7, 5,
           "Bip01 Head", "mouth", caps=(True, True))
    teeth = []
    for i in range(5):
        x = -2.1 + i * (4.2 / 4)
        z = 61.15 + 0.50 * (abs(x) / 4.7) ** 1.7
        y = jaw_y(CX + x, z) - 0.40
        teeth.append((CX + x, y, z))
    b.tube(teeth, [0.14] * 5, [0.16] * 5, 4,
           "Bip01 Head", "teeth", caps=(True, True))
    lower_lip = []
    for i in range(5):
        x = -4.1 + i * (8.2 / 4)
        z = 60.55 + 0.55 * (abs(x) / 4.7) ** 1.7
        y = jaw_y(CX + x, z) - 0.28
        lower_lip.append((CX + x, y, z))
    b.tube(lower_lip, [0.20] * 5, [0.20] * 5, 4,
           "Bone01", "cheek", caps=(True, True))

    # GoldSrc's compiler prunes unused leaf bones.  A tiny dark triangle at
    # each otherwise-unused bone head keeps the exact 55-bone arctic skeleton.
    arm = bpy.data.objects.get(ARM_NAME)
    if arm is not None:
        used = set(b.bones)
        missing = [bone.name for bone in arm.data.bones if bone.name not in used]
        print("BONE KEEPERS:", missing)
        for bone in missing:
            bb = arm.data.bones[bone]
            h = arm.matrix_world @ bb.head_local
            ids = []
            for off in (Vector((0.11, 0.0, 0.0)), Vector((0.0, 0.11, 0.0)),
                        Vector((0.0, 0.0, 0.11))):
                ids.append(b.vert(h + off, bone))
            uv = uv_center("dark")
            b.face(tuple(ids), [uv] * 3, False)

    return b


# ---------------------------------------------------------------------- scene glue
def clear_old():
    old = bpy.data.objects.get(MESH_NAME)
    if old:
        data = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll:
        bpy.data.collections.remove(coll)
    old_mat = bpy.data.materials.get("shrek.bmp")
    if old_mat and old_mat.users == 0:
        bpy.data.materials.remove(old_mat)


def make_material():
    tex_path = os.path.join(ROOT, "textures", "shrek.bmp")
    if not os.path.isfile(tex_path):
        raise FileNotFoundError(tex_path)
    image = bpy.data.images.get("shrek.bmp")
    if image is None:
        image = bpy.data.images.load(tex_path, check_existing=False)
        image.name = "shrek.bmp"
    image.colorspace_settings.name = "sRGB"
    mat = bpy.data.materials.get("shrek.bmp")
    if mat is None:
        mat = bpy.data.materials.new("shrek.bmp")
    mat.use_nodes = True
    mat["goldsrc_texture_token"] = "shrek.bmp"
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None)
    if tex is None:
        tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    bsdf.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.0
    if "Base Color" in bsdf.inputs:
        try:
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        except Exception:
            pass
    out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        out = nodes.new("ShaderNodeOutputMaterial")
    try:
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    except Exception:
        pass
    return mat


def create_object(builder: Builder):
    arm = bpy.data.objects.get(ARM_NAME)
    if arm is None:
        raise RuntimeError(f"missing armature {ARM_NAME}")
    mesh = bpy.data.meshes.new(MESH_NAME)
    mesh.from_pydata([tuple(v) for v in builder.verts], [], builder.faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(MESH_NAME, mesh)
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(coll)
    coll.objects.link(obj)
    mat = make_material()
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for poly, uvs, smooth in zip(mesh.polygons, builder.face_uvs, builder.face_smooth):
        poly.use_smooth = smooth
        for li, co in zip(poly.loop_indices, uvs):
            uv.data[li].uv = co
    # rigid vertex groups
    by_bone: dict[str, list[int]] = {}
    for i, bone in enumerate(builder.bones):
        by_bone.setdefault(bone, []).append(i)
    for bone, ids in by_bone.items():
        group = obj.vertex_groups.new(name=bone)
        group.add(ids, 1.0, "REPLACE")
    obj.parent = arm
    obj.matrix_parent_inverse = arm.matrix_world.inverted()
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    obj.matrix_world = Matrix.Identity(4)
    return obj


def apply_layout():
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name != MESH_NAME:
            obj.hide_render = True
            obj.hide_viewport = True
    obj = bpy.data.objects.get(MESH_NAME)
    if obj:
        obj.hide_render = False
        obj.hide_viewport = False
    bpy.context.scene.frame_set(0)


def build():
    clear_old()
    builder = build_mesh()
    obj = create_object(builder)
    apply_layout()
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    print("BUILD OK", obj.name, "verts", len(obj.data.vertices),
          "polys", len(obj.data.polygons), "tris", tris,
          "groups", len(obj.vertex_groups))
    return obj


if __name__ == "__main__":
    build()
