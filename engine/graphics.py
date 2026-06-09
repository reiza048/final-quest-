# Custom Graphics Engine
import pygame
import math

class GraphicsEngine:

    @staticmethod
    def put_pixel(surface, x, y, color):
        """Plot satu pixel ke surface."""
        x, y = int(x), int(y)
        if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
            surface.set_at((x, y), color)

    @staticmethod
    def put_thick_pixel(surface, x, y, color, thickness=1):
        """Plot pixel dengan ketebalan tertentu."""
        if thickness <= 1:
            GraphicsEngine.put_pixel(surface, x, y, color)
        else:
            half = thickness // 2
            for dx in range(-half, half + 1):
                for dy in range(-half, half + 1):
                    GraphicsEngine.put_pixel(surface, x + dx, y + dy, color)

    @staticmethod
    def draw_line_dda(surface, x1, y1, x2, y2, color, thickness=1):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            GraphicsEngine.put_thick_pixel(surface, x1, y1, color, thickness)
            return

        x_inc = dx / steps
        y_inc = dy / steps
        x, y = float(x1), float(y1)

        for _ in range(int(steps) + 1):
            GraphicsEngine.put_thick_pixel(surface, round(x), round(y), color, thickness)
            x += x_inc
            y += y_inc

    @staticmethod
    def draw_line_bresenham(surface, x1, y1, x2, y2, color, thickness=1):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            GraphicsEngine.put_thick_pixel(surface, x1, y1, color, thickness)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    @staticmethod
    def _bezier_point(control_points, t):
        """Hitung titik Bezier menggunakan algoritma De Casteljau."""
        points = [list(p) for p in control_points]
        n = len(points)
        for r in range(1, n):
            for i in range(n - r):
                points[i][0] = (1 - t) * points[i][0] + t * points[i + 1][0]
                points[i][1] = (1 - t) * points[i][1] + t * points[i + 1][1]
        return (points[0][0], points[0][1])

    @staticmethod
    def draw_bezier(surface, control_points, color, segments=100, thickness=1):
        if len(control_points) < 2:
            return
        prev = control_points[0]
        for i in range(1, segments + 1):
            t = i / segments
            curr = GraphicsEngine._bezier_point(control_points, t)
            GraphicsEngine.draw_line_bresenham(
                surface, int(prev[0]), int(prev[1]),
                int(curr[0]), int(curr[1]), color, thickness
            )
            prev = curr

    @staticmethod
    def _bspline_basis(i, k, t, knots):
        """Fungsi basis B-Spline rekursif (Cox-de Boor)."""
        if k == 1:
            return 1.0 if knots[i] <= t < knots[i + 1] else 0.0
        d1 = knots[i + k - 1] - knots[i]
        d2 = knots[i + k] - knots[i + 1]
        c1 = ((t - knots[i]) / d1 * GraphicsEngine._bspline_basis(i, k - 1, t, knots)) if d1 != 0 else 0.0
        c2 = ((knots[i + k] - t) / d2 * GraphicsEngine._bspline_basis(i + 1, k - 1, t, knots)) if d2 != 0 else 0.0
        return c1 + c2

    @staticmethod
    def draw_bspline(surface, control_points, color, degree=3, segments=100, thickness=1):
        """Kurva B-Spline dengan knot vector uniform."""
        n = len(control_points)
        if n < degree + 1:
            GraphicsEngine.draw_bezier(surface, control_points, color, segments, thickness)
            return
        k = degree + 1
        knots = [0] * k + list(range(1, n - degree)) + [n - degree] * k
        prev = None
        for i in range(segments + 1):
            t = knots[k - 1] + (knots[n] - knots[k - 1]) * i / segments
            if t >= knots[n]:
                t = knots[n] - 0.0001
            x, y = 0.0, 0.0
            for j in range(n):
                basis = GraphicsEngine._bspline_basis(j, k, t, knots)
                x += basis * control_points[j][0]
                y += basis * control_points[j][1]
            curr = (int(x), int(y))
            if prev is not None:
                GraphicsEngine.draw_line_bresenham(
                    surface, prev[0], prev[1], curr[0], curr[1], color, thickness
                )
            prev = curr

    @staticmethod
    def flood_fill(surface, x, y, fill_color):
        x, y = int(x), int(y)
        if x < 0 or x >= surface.get_width() or y < 0 or y >= surface.get_height():
            return
        target_color = tuple(surface.get_at((x, y))[:3])
        fill_rgb = tuple(fill_color[:3])
        if target_color == fill_rgb:
            return
        stack = [(x, y)]
        visited = set()
        w, h = surface.get_width(), surface.get_height()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            if tuple(surface.get_at((cx, cy))[:3]) != target_color:
                continue
            surface.set_at((cx, cy), fill_color)
            visited.add((cx, cy))
            stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

    @staticmethod
    def scanline_fill(surface, polygon_points, color):
        if len(polygon_points) < 3:
            return
        min_y = int(min(p[1] for p in polygon_points))
        max_y = int(max(p[1] for p in polygon_points))
        n = len(polygon_points)

        for y in range(min_y, max_y + 1):
            intersections = []
            for i in range(n):
                x1, y1 = polygon_points[i]
                x2, y2 = polygon_points[(i + 1) % n]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)
            intersections.sort()
            for i in range(0, len(intersections) - 1, 2):
                x_start = int(math.ceil(intersections[i]))
                x_end = int(math.floor(intersections[i + 1]))
                for x in range(x_start, x_end + 1):
                    GraphicsEngine.put_pixel(surface, x, y, color)

    @staticmethod
    def draw_circle(surface, cx, cy, radius, color, thickness=1, fill=False):
        """Midpoint Circle Algorithm dengan simetri 8-arah."""
        cx, cy, radius = int(cx), int(cy), int(radius)
        if fill:
            for y_off in range(-radius, radius + 1):
                half_w = int(math.sqrt(max(0, radius * radius - y_off * y_off)))
                for x in range(cx - half_w, cx + half_w + 1):
                    GraphicsEngine.put_pixel(surface, x, cy + y_off, color)
            return

        x, y, d = 0, radius, 1 - radius

        def _plot8(cx, cy, x, y):
            for px, py in [(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                           (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]:
                GraphicsEngine.put_thick_pixel(surface, px, py, color, thickness)

        _plot8(cx, cy, x, y)
        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            _plot8(cx, cy, x, y)

    @staticmethod
    def draw_dashed_line(surface, x1, y1, x2, y2, color, dash=8, gap=4, thickness=1):
        """Garis putus-putus (dashed line)."""
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        pos = 0
        drawing = True
        while pos < length:
            seg = dash if drawing else gap
            end = min(pos + seg, length)
            if drawing:
                GraphicsEngine.draw_line_bresenham(
                    surface,
                    int(x1 + ux * pos), int(y1 + uy * pos),
                    int(x1 + ux * end), int(y1 + uy * end),
                    color, thickness
                )
            pos = end
            drawing = not drawing

    @staticmethod
    def draw_dotted_line(surface, x1, y1, x2, y2, color, spacing=4, thickness=1):
        """Garis titik-titik (dotted line)."""
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        pos = 0
        while pos < length:
            GraphicsEngine.put_thick_pixel(
                surface, int(x1 + ux * pos), int(y1 + uy * pos), color, thickness
            )
            pos += spacing

    @staticmethod
    def draw_rect(surface, x, y, w, h, color, thickness=1, style='solid'):
        """Rectangle menggunakan Bresenham lines."""
        draw_fn = GraphicsEngine.draw_line_bresenham
        if style == 'dashed':
            draw_fn = lambda s, x1, y1, x2, y2, c, t: GraphicsEngine.draw_dashed_line(s, x1, y1, x2, y2, c, thickness=t)
        elif style == 'dotted':
            draw_fn = lambda s, x1, y1, x2, y2, c, t: GraphicsEngine.draw_dotted_line(s, x1, y1, x2, y2, c, thickness=t)
        draw_fn(surface, x, y, x + w, y, color, thickness)
        draw_fn(surface, x + w, y, x + w, y + h, color, thickness)
        draw_fn(surface, x + w, y + h, x, y + h, color, thickness)
        draw_fn(surface, x, y + h, x, y, color, thickness)

    @staticmethod
    def fill_rect(surface, x, y, w, h, color):
        """Fill rectangle solid."""
        for py in range(int(y), int(y + h)):
            for px in range(int(x), int(x + w)):
                GraphicsEngine.put_pixel(surface, px, py, color)

    @staticmethod
    def draw_gradient_rect(surface, x, y, w, h, color1, color2, vertical=False):
        """Rectangle dengan gradient fill."""
        for i in range(int(h) if vertical else int(w)):
            t = i / (h if vertical else w) if (h if vertical else w) > 0 else 0
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            c = (r, g, b)
            if vertical:
                for px in range(int(x), int(x + w)):
                    GraphicsEngine.put_pixel(surface, px, int(y) + i, c)
            else:
                for py in range(int(y), int(y + h)):
                    GraphicsEngine.put_pixel(surface, int(x) + i, py, c)

    @staticmethod
    def draw_polygon(surface, points, color, thickness=1):
        """Gambar outline polygon."""
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            GraphicsEngine.draw_line_bresenham(surface, x1, y1, x2, y2, color, thickness)

    @staticmethod
    def fast_fill_rect(surface, x, y, w, h, color):
        """Versi cepat fill rect menggunakan pygame.draw (untuk UI)."""
        pygame.draw.rect(surface, color, (int(x), int(y), int(w), int(h)))

    @staticmethod
    def fast_line(surface, x1, y1, x2, y2, color, thickness=1):
        """Versi cepat line menggunakan pygame.draw (untuk performa)."""
        pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), int(thickness))

    @staticmethod
    def draw_gradient_rect_fast(surface, x, y, w, h, color1, color2, vertical=False):
        """Gradient rect yang lebih cepat menggunakan pygame.draw."""
        steps = int(h if vertical else w)
        if steps <= 0:
            return
        for i in range(steps):
            t = i / steps
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            if vertical:
                pygame.draw.line(surface, (r, g, b), (int(x), int(y) + i), (int(x + w), int(y) + i))
            else:
                pygame.draw.line(surface, (r, g, b), (int(x) + i, int(y)), (int(x) + i, int(y + h)))
