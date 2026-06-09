"""
engine/transform.py - Transformasi 2D
=====================================
Implementasi transformasi geometri 2D menggunakan matriks homogen 3x3.

Transformasi yang diimplementasikan:
1. Translasi (pergeseran posisi)
2. Rotasi (perputaran terhadap titik pusat)
3. Scaling (perubahan ukuran)
4. Komposisi transformasi
"""

import math
import numpy as np
import pygame


class Transform2D:
    """Transformasi 2D menggunakan matriks homogen 3x3."""

    # ============================================================
    # MATRIKS TRANSFORMASI
    # ============================================================

    @staticmethod
    def translation_matrix(tx, ty):
        """
        Matriks translasi 3x3.
        | 1  0  tx |
        | 0  1  ty |
        | 0  0  1  |
        """
        return np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ], dtype=float)

    @staticmethod
    def rotation_matrix(angle_deg):
        """
        Matriks rotasi 3x3 (berlawanan arah jarum jam).
        | cos  -sin  0 |
        | sin   cos  0 |
        |  0     0   1 |
        """
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a,  cos_a, 0],
            [0,      0,     1]
        ], dtype=float)

    @staticmethod
    def scale_matrix(sx, sy):
        """
        Matriks scaling 3x3.
        | sx  0  0 |
        |  0 sy  0 |
        |  0  0  1 |
        """
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0,  0, 1]
        ], dtype=float)

    # ============================================================
    # OPERASI TRANSFORMASI PADA TITIK
    # ============================================================

    @staticmethod
    def apply_matrix(points, matrix):
        """
        Terapkan matriks transformasi pada list of points.
        points: list of (x, y) tuples
        matrix: numpy 3x3 matrix
        Returns: list of (x, y) tuples
        """
        result = []
        for x, y in points:
            p = np.array([x, y, 1], dtype=float)
            transformed = matrix @ p
            result.append((transformed[0], transformed[1]))
        return result

    @staticmethod
    def translate(points, tx, ty):
        """Translasi semua titik sebesar (tx, ty)."""
        mat = Transform2D.translation_matrix(tx, ty)
        return Transform2D.apply_matrix(points, mat)

    @staticmethod
    def rotate(points, angle_deg, center=(0, 0)):
        """
        Rotasi semua titik sebesar angle_deg derajat terhadap center.
        Langkah: translate ke origin → rotasi → translate kembali
        """
        cx, cy = center
        mat = (
            Transform2D.translation_matrix(cx, cy) @
            Transform2D.rotation_matrix(angle_deg) @
            Transform2D.translation_matrix(-cx, -cy)
        )
        return Transform2D.apply_matrix(points, mat)

    @staticmethod
    def scale(points, sx, sy, center=(0, 0)):
        """
        Scaling semua titik dengan faktor (sx, sy) terhadap center.
        Langkah: translate ke origin → scale → translate kembali
        """
        cx, cy = center
        mat = (
            Transform2D.translation_matrix(cx, cy) @
            Transform2D.scale_matrix(sx, sy) @
            Transform2D.translation_matrix(-cx, -cy)
        )
        return Transform2D.apply_matrix(points, mat)

    @staticmethod
    def compose(*matrices):
        """Komposisi beberapa matriks transformasi (kanan ke kiri)."""
        result = np.eye(3)
        for m in matrices:
            result = result @ m
        return result

    # ============================================================
    # TRANSFORMASI SURFACE / SPRITE
    # ============================================================

    @staticmethod
    def transform_surface(surface, angle=0, scale_factor=1.0, flip_x=False, flip_y=False):
        """
        Transformasi pygame surface (sprite).
        - angle: rotasi dalam derajat
        - scale_factor: faktor scaling (1.0 = normal)
        - flip_x/flip_y: mirror horizontal/vertikal
        """
        result = surface
        if flip_x or flip_y:
            result = pygame.transform.flip(result, flip_x, flip_y)
        if scale_factor != 1.0:
            w = int(result.get_width() * scale_factor)
            h = int(result.get_height() * scale_factor)
            if w > 0 and h > 0:
                result = pygame.transform.scale(result, (w, h))
        if angle != 0:
            result = pygame.transform.rotate(result, angle)
        return result

    @staticmethod
    def lerp(a, b, t):
        """Linear interpolation antara a dan b."""
        return a + (b - a) * t

    @staticmethod
    def lerp_point(p1, p2, t):
        """Linear interpolation antara dua titik."""
        return (
            Transform2D.lerp(p1[0], p2[0], t),
            Transform2D.lerp(p1[1], p2[1], t)
        )

    @staticmethod
    def lerp_color(c1, c2, t):
        """Linear interpolation antara dua warna."""
        t = max(0, min(1, t))
        return (
            int(Transform2D.lerp(c1[0], c2[0], t)),
            int(Transform2D.lerp(c1[1], c2[1], t)),
            int(Transform2D.lerp(c1[2], c2[2], t))
        )
