import time
import bpy
import bmesh
import math
from bpy_extras.object_utils import (
        AddObjectHelper,
        object_data_add,
)
from bpy.props import (
        EnumProperty,
        BoolProperty,
        IntProperty,
        FloatProperty,
)
import numpy as np

bl_info = {
    "name": "Tile Regular Polygons",
    "author": "PG0721",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Regular polygon tiling add-on",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "https://olj611.hatenablog.com/entry/2024/09/06/133301",
    "tracker_url": "https://olj611.hatenablog.com/entry/2024/09/06/133301",
    "category": "Add Mesh"
}

class UniformTilings:
    __sqrt2 = math.sqrt(2)
    __sqrt3 = math.sqrt(3)    
    __cos15 = math.cos(15 / 180 * math.pi)
    __sin15 = math.sin(15 / 180 * math.pi)
    __tan15 = math.tan(15 / 180 * math.pi)
    __cos30 = math.cos(30 / 180 * math.pi)
    __sin30 = math.sin(30 / 180 * math.pi)
    __tan30 = math.tan(30 / 180 * math.pi)
    __cos45 = math.cos(45 / 180 * math.pi)
    __sin45 = math.sin(45 / 180 * math.pi)
    __tan45 = math.tan(45 / 180 * math.pi)
    __cos60 = math.cos(60 / 180 * math.pi)
    __sin60 = math.sin(60 / 180 * math.pi)
    __tan60 = math.tan(60 / 180 * math.pi)
    __cos67_5 = math.cos(67.5 / 180 * math.pi)
    __sin67_5 = math.sin(67.5 / 180 * math.pi)
    __tan67_5 = math.tan(67.5 / 180 * math.pi)
    __cos75 = math.cos(75 / 180 * math.pi)
    __sin75 = math.sin(75 / 180 * math.pi)
    __tan75 = math.tan(75 / 180 * math.pi)
    __cos120 = math.cos(120 / 180 * math.pi)
    __sin120 = math.sin(120 / 180 * math.pi)
    __cos180 = math.cos(180 / 180 * math.pi)
    __sin180 = math.sin(180 / 180 * math.pi)
    __cos240 = math.cos(240 / 180 * math.pi)
    __sin240 = math.sin(240 / 180 * math.pi)

    def create(tiling_type, edge_length, gap, ratio_type, ratio_target, ratio, range_x, range_y):
        ut = UniformTilings
        radius_distance = ut.__radius_distance
        same_distance_ratio = ut.__same_distance_ratio
        get_rhombitrihexagonal_ratios = ut.__get_rhombitrihexagonal_ratios
        get_ratios = ut.__get_ratios
        is_enable_edge_ratio = ut.__is_enable_edge_ratio
        create_faces = UniformTilings.__create_faces
        start = time.time()

        lut = {
            "3.3.3.3.3.3": {
                "tile": ut.__triangular_tiling,
                "num": (3,)
            },
            "4.4.4.4": {
                "tile": ut.__square_tiling,
                "num": (4,)
            },
            "6.6.6": {
                "tile": ut.__hexagonal_tiling,
                "num": (6,)
            },
            "(3.6)^2": {
                "tile": ut.__trihexagonal_tiling,
                "num": (6, 3, 3)
            },
            "3.3.4.3.4": {
                "tile": ut.__snub_square_tiling,
                "num": (4, 3, 3)
            },
            "4.8.8": {
                "tile": ut.__truncated_square_tiling,
                "num": (8, 4)
            },
            "3.12.12": {
                "tile": ut.__truncated_hexagonal_tiling,
                "num": (12, 3, 3)
            },
            "3.4.6.4": {
                "tile": ut.__rhombitrihexagonal_tiling,
                "num": (6, 4, 3, 4, 3, 4)
            },
            "4.6.12": {
                "tile": ut.__truncated_trihexagonal_tiling,
                "num": (12, 4, 6, 4, 6, 4)
            },
            "3.3.3.3.6": {
                "tile": ut.__snub_hexagonal_tiling,
                "num": (6, 3, 3, 3, 3, 3, 3, 3, 3)
            },
            "3.3.3.4.4": {
                "tile": ut.__elongated_triangular_tiling,
                "num": (4, 3, 3)
            },
        }
        ut.__tri_r, ut.__tri_d = radius_distance(3, edge_length)
        ut.__tri_ratio = same_distance_ratio(3, gap, edge_length)
        ut.__sq_r, ut.__sq_d = radius_distance(4, edge_length)
        ut.__sq_ratio = same_distance_ratio(4, gap, edge_length)
        ut.__hex_r, ut.__hex_d = radius_distance(6, edge_length)
        ut.__hex_ratio = same_distance_ratio(6, gap, edge_length)
        ut.__oct_r, ut.__oct_d = radius_distance(8, edge_length)
        ut.__oct_ratio = same_distance_ratio(8, gap, edge_length)
        ut.__dodec_r, ut.__dodec_d = radius_distance(12, edge_length)
        ut.__dodec_ratio = same_distance_ratio(12, gap, edge_length)

        # ratio except same distance
        if is_enable_edge_ratio(tiling_type) and ratio_type != "distance":
            if tiling_type == "3.4.6.4":
                ratios =  get_rhombitrihexagonal_ratios(gap, edge_length, ratio_type, ratio_target, ratio)
                ut.__tri_ratio, ut.__sq_ratio, ut.__hex_ratio = ratios
            else:
                ratios = get_ratios(tiling_type, gap, edge_length, ratio_type, ratio)
                if tiling_type == "(3.6)^2":
                    ut.__tri_ratio, ut.__hex_ratio = ratios
                elif tiling_type == "4.8.8":
                    ut.__sq_ratio, ut.__oct_ratio = ratios
                elif tiling_type == "3.12.12":
                    ut.__tri_ratio, ut.__dodec_ratio = ratios

        # create vertices
        vertices = []
        for i in range(*range_y):
            for j in range(*range_x):
                vertices += lut[tiling_type]["tile"](j, i, edge_length, gap)

        # create faces
        iteration_count = len(range(*range_y)) * len(range(*range_x))
        faces = create_faces(iteration_count, lut[tiling_type]["num"])

        end = time.time()
        time_diff = end - start
        #print(time_diff)
        return vertices, faces
    
    def __triangular_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        create_vertices = ut.__create_vertices

        # triangle
        start_angle = math.pi * 0.5
        if idx_y % 2 != 0:
            start_angle += math.pi
        if idx_x % 2 != 0:
            start_angle += math.pi
        x = 0.5 * length * idx_x        
        if idx_y % 2 == 0:
            y = (tri_r + tri_d) * idx_y
            if idx_x % 2 != 0:
                y += tri_r - tri_d
        else:
            t_idx_y = idx_y - 1
            y = (tri_r + tri_d) * t_idx_y
            y += 2 * tri_r 
            if idx_x % 2 != 0:
                y -= tri_r - tri_d
        return create_vertices(3, x, y, tri_r * tri_ratio, start_angle)
    
    def __square_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        create_vertices = ut.__create_vertices

        # square
        start_angle = math.pi * 0.25
        x = length * idx_x
        y = length * idx_y
        return create_vertices(4, x, y, sq_r * sq_ratio, start_angle)
    
    def __hexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        hex_r, hex_d, hex_ratio = ut.__hex_r, ut.__hex_d, ut.__hex_ratio
        create_vertices = ut.__create_vertices

        # hexagon
        start_angle = math.pi * 0.5
        x = 2 * hex_d * idx_x
        if idx_y % 2 != 0:
            x += hex_d
        y = 3 / 2 * hex_r * idx_y
        return create_vertices(6, x, y, hex_r * hex_ratio, start_angle)
    
    def __trihexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        sqrt3 = ut.__sqrt3
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        hex_r, hex_d, hex_ratio = ut.__hex_r, ut.__hex_d, ut.__hex_ratio
        create_vertices = UniformTilings.__create_vertices

        # hexagon
        start_angle = math.pi * 0.5
        x = 2 * hex_d * idx_x
        y = 2 * hex_r * idx_y
        if idx_x % 2 != 0:
            y += hex_r        
        vertices = create_vertices(6, x, y, hex_r * hex_ratio, start_angle)        
        hex_x = x
        hex_y = y
        
        # right triangle
        start_angle = math.pi / 3
        x = hex_x + (hex_d + tri_d) * 0.5
        y = hex_y + (hex_d + tri_d) * sqrt3 * 0.5  
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        # left triangle
        start_angle = 2 * math.pi / 3
        x = hex_x - (hex_d + tri_d) * 0.5
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        return vertices
        
    def __snub_square_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        cos15 = ut.__cos15
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        create_vertices = ut.__create_vertices

        # square
        start_angle = math.pi * 15 / 180
        if idx_y % 2 != 0:
            start_angle *= -1
        if idx_x % 2 != 0:
            start_angle *= -1
        x = 2 * sq_r * cos15 * idx_x
        y = 2 * sq_r * cos15 * idx_y        
        vertices = create_vertices(4, x, y, sq_r * sq_ratio, start_angle)
        sq_x = x
        sq_y = y

        # right triangle
        angle = -30
        if idx_y % 2 != 0:
            angle += 60
        if idx_y % 2 == 0:
            if idx_x % 2 != 0:
                angle += 60
        else:
            if idx_x % 2 != 0:
                angle -= 60
        start_angle = math.pi * angle / 180
        cos = math.cos(angle / 180 * math.pi)
        sin = math.sin(angle / 180 * math.pi)
        x = sq_x + (sq_d + tri_d) * cos
        y = sq_y + (sq_d + tri_d) * sin
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        # left triangle
        angle += 90
        start_angle = math.pi * angle / 180
        cos = math.cos(angle / 180 * math.pi)
        sin = math.sin(angle / 180 * math.pi)
        x = sq_x + (sq_d + tri_d) * cos
        y = sq_y + (sq_d + tri_d) * sin
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)
        
        return vertices

    def __truncated_square_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        oct_r, oct_d, oct_ratio = ut.__oct_r, ut.__oct_d, ut.__oct_ratio
        create_vertices = ut.__create_vertices

        # octagon
        start_angle = math.pi * 22.5 / 180
        x = 2 * (oct_d + length * 0.5) * idx_x
        if idx_y % 2 != 0:
            x += oct_d + length * 0.5
        y = (oct_d + length * 0.5) * idx_y
        vertices = create_vertices(8, x, y, oct_r * oct_ratio, start_angle)

        # square
        start_angle = math.pi * 0.25
        y += oct_d + length * 0.5        
        vertices += UniformTilings.__create_vertices(4, x, y, sq_r * sq_ratio, start_angle)

        return vertices
    
    def __truncated_hexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        sqrt3 = ut.__sqrt3
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        dodec_r, dodec_d, dodec_ratio = ut.__dodec_r, ut.__dodec_d, ut.__dodec_ratio
        create_vertices = ut.__create_vertices

        # dodecagon
        start_angle = math.pi / 12
        x = 2 * dodec_d * sqrt3 / 2 * idx_x
        y = 2 * dodec_d * idx_y
        if idx_x % 2 != 0:
            y += dodec_d        
        vertices = create_vertices(12, x, y, dodec_r * dodec_ratio, start_angle)
        dodec_x = x
        dodec_y = y

        # right triangle
        start_angle = math.pi / 3
        x = dodec_x + (dodec_d + tri_d) * 0.5
        y = dodec_y + (dodec_d + tri_d) * sqrt3 / 2        
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        # left triangle
        start_angle = math.pi * 2 / 3
        x = dodec_x - (dodec_d + tri_d) * 0.5
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        return vertices
        
    def __rhombitrihexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        cos30, sin30 = ut.__cos30, ut.__sin30
        cos120, sin120 = ut.__cos120, ut.__sin120
        cos180, sin180 = ut.__cos180, ut.__sin180
        cos240, sin240 = ut.__cos240, ut.__sin240
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        hex_r, hex_d, hex_ratio = ut.__hex_r, ut.__hex_d, ut.__hex_ratio
        create_vertices = ut.__create_vertices

        # hexagon
        start_angle = 0
        x = (hex_r + tri_r + tri_d + sq_d) * idx_x
        y = 2 * (hex_d + sq_d) * idx_y
        if idx_x % 2 != 0:
            y += hex_d + sq_d
        vertices = create_vertices(6, x, y, hex_r * hex_ratio, start_angle)

        # square #0
        start_angle = 75 / 180 * math.pi
        x += (hex_d + sq_d) * cos30
        y += (hex_d + sq_d) * sin30
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)

        # triangle #0
        start_angle = 120 / 180 * math.pi
        x += (sq_d + tri_d) * cos120
        y += (sq_d + tri_d) * sin120
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        # square #1
        start_angle = 135 / 180 * math.pi
        x += (sq_d + tri_d) * cos180
        y += (sq_d + tri_d) * sin180
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)

        # triangle #1
        start_angle = 180 / 180 * math.pi
        x += (sq_d + tri_d) * cos180
        y += (sq_d + tri_d) * sin180
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        # square #2
        start_angle = 195 / 180 * math.pi
        x += (sq_d + tri_d) * cos240
        y += (sq_d + tri_d) * sin240
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)

        return vertices

    def __truncated_trihexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        hex_r, hex_d, hex_ratio = ut.__hex_r, ut.__hex_d, ut.__hex_ratio
        dodec_r, dodec_d, dodec_ratio = ut.__dodec_r, ut.__dodec_d, ut.__dodec_ratio
        create_vertices = ut.__create_vertices

        # dodecagon        
        start_angle = math.pi / 12
        x = (dodec_d + 2 * hex_d + sq_d) * idx_x
        y = 2 * (dodec_d + sq_d) * idx_y
        if idx_x % 2 != 0:
            y += dodec_d + dodec_r * math.sin(15 / 180 * math.pi)        
        vertices = create_vertices(12, x, y, dodec_r * dodec_ratio, start_angle)

        # hexagon and square
        cos30 = UniformTilings.__cos30
        sin30 = UniformTilings.__sin30
        cos60 = UniformTilings.__cos60
        sin60 = UniformTilings.__sin60
        cos120 = UniformTilings.__cos120
        sin120 = UniformTilings.__sin120
        cos180 = UniformTilings.__cos180
        sin180 = UniformTilings.__sin180
        cos240 = UniformTilings.__cos240
        sin240 = UniformTilings.__sin240
        outer_length = hex_d + sq_d        
        
        # square #0
        start_angle = 75 / 180 * math.pi
        x += (dodec_d + sq_d) * cos30
        y += (dodec_d + sq_d) * sin30
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)
        # hexagon #0
        start_angle = math.pi * 0.5
        x += outer_length * cos120
        y += outer_length * sin120
        vertices += create_vertices(6, x, y, hex_r * hex_ratio, start_angle)
        # square #1
        start_angle = 135 / 180 * math.pi
        x += outer_length * cos180
        y += outer_length * sin180
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)
        # hexagon #1
        start_angle = math.pi * 0.5
        x += outer_length * cos180
        y += outer_length * sin180
        vertices += create_vertices(6, x, y, hex_r * hex_ratio, start_angle)
        # square #2
        start_angle = 195 / 180 * math.pi
        x += outer_length * cos240
        y += outer_length * sin240
        vertices += create_vertices(4, x, y, sq_r * sq_ratio, start_angle)

        return vertices

    def __snub_hexagonal_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        cos30, sin30 = ut.__cos30, ut.__sin30
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        hex_r, hex_d, hex_ratio = ut.__hex_r, ut.__hex_d, ut.__hex_ratio        
        create_vertices = ut.__create_vertices

        # hexagon
        start_angle = 0
        x = -0.5 * hex_r * idx_y + 2.5 * hex_r * idx_x
        y = 3 * hex_d * idx_y - hex_d * idx_x        
        vertices = create_vertices(6, x, y, hex_r * hex_ratio, start_angle)
        hex_x = x
        hex_y = y

        # triangle
        x = 0
        y = 0
        for i in range(8):
            if i % 2 == 0:
                start_angle = math.pi * (30 + 180) / 180
            else:
                start_angle = math.pi * 30 / 180
            if i == 0:
                x += hex_x + (hex_d + tri_d) * cos30
                y += hex_y + (hex_d + tri_d) * sin30 - 2 * tri_d - tri_r
            elif i == 1:
                y += 2 * tri_d + tri_r
            elif i == 2:
                y += 2 * tri_d
            elif i == 3 or i == 5:
                x += - 0.5 * length
                y += tri_r - tri_d
            elif i == 4 or i == 6:
                x += - 0.5 * length
                y += tri_d - tri_r
            elif i == 7:
                y += - 2 * tri_d
            vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)
                 
        return vertices
    
    def __elongated_triangular_tiling(idx_x, idx_y, length, gap):
        ut = UniformTilings
        cos30 = ut.__cos30
        tri_r, tri_d, tri_ratio = ut.__tri_r, ut.__tri_d, ut.__tri_ratio
        sq_r, sq_d, sq_ratio = ut.__sq_r, ut.__sq_d, ut.__sq_ratio
        create_vertices = ut.__create_vertices

        # square
        start_angle = math.pi * 0.25
        x = length * idx_x
        if idx_y % 2 != 0:
            x += 0.5 * length
        y = length * (1 + cos30) * idx_y        
        vertices = create_vertices(4, x, y, sq_r * sq_ratio, start_angle)
        
        # left triangle
        start_angle = math.pi * 90 / 180
        y += sq_d + tri_d
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)
        
        # right triangle
        start_angle = math.pi * (-90) / 180
        x += length * 0.5
        y += tri_r - tri_d
        vertices += create_vertices(3, x, y, tri_r * tri_ratio, start_angle)

        return vertices
    
    def __radius_distance(count, length):
        half_len = 0.5 * length
        cos30 = UniformTilings.__cos30
        tan30 = UniformTilings.__tan30
        cos45 = UniformTilings.__cos45
        tan45 = UniformTilings.__tan45
        cos60 = UniformTilings.__cos60
        tan60 = UniformTilings.__tan60
        cos67_5 = UniformTilings.__cos67_5
        tan67_5 = UniformTilings.__tan67_5
        cos75 = UniformTilings.__cos75
        tan75 = UniformTilings.__tan75
        if count == 3:
            radius = half_len / cos30
            distance = half_len * tan30
        elif count == 4:
            radius = half_len / cos45
            distance = half_len
        elif count == 6:
            radius = half_len / cos60
            distance = half_len * tan60
        elif count == 8:
            radius = half_len / cos67_5
            distance = half_len * tan67_5
        elif count == 12:
            radius = half_len / cos75
            distance = half_len * tan75
        else:
            theta = math.pi * (0.5 - 1 / count)
            radius = half_len / math.cos(theta)
            distance = half_len * math.tan(theta)
        return radius, distance
    
    def __get_rhombitrihexagonal_ratios(gap, length, ratio_type, ratio_target, ratio):
        half_len = 0.5 * length
        tan30 = UniformTilings.__tan30
        tan45 = UniformTilings.__tan45
        tan60 = UniformTilings.__tan60
        g = gap
        
        a = ratio if ratio_type == "input" else 1
        
        d3 = half_len * tan30
        d4 = half_len * tan45
        d6 = half_len * tan60

        d = np.array([
            [d3 + d4 - g],
            [d4 + d6 - g],
            [0]
        ])        
        if ratio_target == "3,4":
            r = np.array([a, -1, 0])
        elif ratio_target == "4,6":
            r = np.array([0, a, -1])
        else:
            r = np.array([a, 0, -1])
        m = np.array([
            [ d3, d4,  0 ], 
            [  0, d4, d6 ],
        ])
        m = np.insert(m, 2, r, axis=0)
        m_inv = np.linalg.pinv(m)        
        s = (m_inv @ d).reshape(3,)        
        return (float(s[0]), float(s[1]), float(s[2]))
    
    def __get_ratios(tiling_type, gap, length, ratio_type, ratio):
        half_len = 0.5 * length
        tan30 = UniformTilings.__tan30
        tan45 = UniformTilings.__tan45
        tan60 = UniformTilings.__tan60
        tan67_5 = UniformTilings.__tan67_5
        tan75 = UniformTilings.__tan75
        g = gap

        a = ratio if ratio_type == "input" else 1

        if tiling_type == "(3.6)^2":
            d0 = half_len * tan30
            d1 = half_len * tan60
        elif tiling_type == "4.8.8":
            d0 = half_len * tan45
            d1 = half_len * tan67_5
        elif tiling_type == "3.12.12":
            d0 = half_len * tan30
            d1 = half_len * tan75
        else: # debug
            d0 = half_len
            d1 = half_len
        
        s0 = 1 / (d0 + a * d1) * (d0 + d1 - g)
        s1 = 1 / (d0 + a * d1) * a * (d0 + d1 - g)
        return (s0, s1)

    def __same_distance_ratio(count, gap, length):
        sqrt3 = UniformTilings.__sqrt3
        tan67_5 = UniformTilings.__tan67_5
        if count == 3:
            return 1 - sqrt3 * gap / length
        elif count == 4:
            return 1 - gap / length
        elif count == 6:
            return 1 - 1 / sqrt3 * gap / length
        elif count == 8:
            return 1 - 1 / tan67_5 * gap / length
        elif count == 12:
            return 1 - 1 / (2 + sqrt3) * gap / length

    def __create_vertices(count, center_x, center_y, radius, start_angle):
        vertices = []
        delta_angle = 2 * math.pi / count
        for i in range(count):
            x = center_x + radius * math.cos(delta_angle * i + start_angle)
            y = center_y + radius * math.sin(delta_angle * i + start_angle)
            vertices.append((x, y, 0))
        return vertices
        
    def __create_faces(iteration_count, kinds):
        index = 0
        faces = [None] * (iteration_count * len(kinds))
        for i in range(iteration_count):
            for j, count in enumerate(kinds):
                face = [None] * count
                for k in range(count):
                    face[k] = index
                    index += 1
                faces[i * len(kinds) + j] = face
        return faces
    
    def __is_enable_edge_ratio(tiling_type):
        return tiling_type in ("(3.6)^2", "4.8.8", "3.12.12", "3.4.6.4")
    
class OBJECT_OT_tile_regular_polygons(bpy.types.Operator, AddObjectHelper):
    bl_idname = "mesh.tile_regular_polygons"
    bl_label = "Tile Regular Polygons"
    bl_description = "Tile Regular Polygons"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Tiliing Type
    tiling_type: EnumProperty(
        name = "Tiling Type", description = "Euclidean uniform tilings type",
        items = [
            ("3.3.3.3.3.3", "Triangular tiling", ""),
            ("4.4.4.4", "Square tiling", ""),
            ("6.6.6", "Hexagonal tiling", ""),
            ("(3.6)^2", "Trihexagonal tiling", ""),
            ("3.3.4.3.4", "Snub square tiling", ""),
            ("4.8.8", "Truncated square tiling", ""),
            ("3.12.12", "Truncated hexagonal tiling", ""),
            ("3.4.6.4", "Rhombitrihexagonal tiling", ""),
            ("4.6.12", "Truncated trihexagonal tiling", ""),
            ("3.3.3.3.6", "Snub hexagonal tiling", ""),
            ("3.3.3.4.4", "Elongated triangular tiling", "")
        ],
        default = "6.6.6"
    ) # type: ignore

    # Edge Length
    edge_length: FloatProperty(
        name = "Edge Length", description = "Polygon edge length when gap is zero",
        default = 1.0, min = 0.001, max = 10000.0, unit = "LENGTH", precision = 3
    ) # type: ignore

    # Gap
    gap: FloatProperty(
        name = "Gap", description = "Width of the gap between polygons.\nIf this value is zero, the vertices will be duplicated",
        default = 0.2, min = 0.0, max = 10000.0, unit = "LENGTH", precision = 3
    ) # type: ignore

    # Ratio Type
    ratio_type: EnumProperty(
        name = "Ratio Type", description = "Polygon Ratio type",
        items = [
            ("distance", "Same Distance", ""),
            ("length", "Same Length", ""),
            ("input", "Input Ratio", "")
        ],
        default = "distance"
    ) # type: ignore

    # Ratio Target
    ratio_target: EnumProperty(
        name = "Ratio Target", description = "Which polygon's ratio",
        items = [
            ("3,4", "Triangle To Square", ""),
            ("4,6", "Square To Hexagon", ""),
            ("3,6", "Triangle To Hexagon", "")
        ],
        default = "4,6"
    ) # type: ignore
    
    # Ratio
    ratio: FloatProperty(
        name = "Ratio", description = "Polygon Ratio",
        default = 1.0, min = 0.01, max = 100.0, precision = 3
    ) # type: ignore
    
    # X Start
    start_x: IntProperty(
        name = "Iteration X Start", description = "Start of iteration X.\nSimilar to the first argument of Python's range method",
        default = -1, min = -32, max = 32
    ) # type: ignore

    # X End
    end_x: IntProperty(
        name = "End", description = "End of iteration X.\nSimilar to the second argument of Python's range method",
        default = 2, min = -32, max = 32
    ) # type: ignore
    
    # X Step
    step_x: IntProperty(
        name = "Step", description = "Step of iteration X.\nSimilar to the third argument of Python's range method",
        default = 1, min = 1, max = 32
    ) # type: ignore
    
    # Y Start
    start_y: IntProperty(
        name = "Iteration Y Start", description = "Start of iteration Y.\nSimilar to the first argument of Python's range method",
        default = -1, min = -32, max = 32
    ) # type: ignore

    # Y End
    end_y: IntProperty(
        name = "End", description = "End of iteration Y.\nSimilar to the second argument of Python's range method",
        default = 2, min = -32, max = 32
    ) # type: ignore
    
    # Y Step
    step_y: IntProperty(
        name = "Step", description = "Step of iteration Y.\nSimilar to the third argument of Python's range method",
        default = 1, min = 1, max = 32
    ) # type: ignore

    # Generate UVs
    uv: BoolProperty(
        name = "Generate UVs",
        description = "Generate a default UV map",
        default = True
    ) # type: ignore
    
    def __is_enable_edge_ratio(self):
        return self.tiling_type in ("(3.6)^2", "4.8.8", "3.12.12", "3.4.6.4")
    
    def __is_enable_input_edge_ratio(self):
        return self.ratio_type == "input" and self.__is_enable_edge_ratio()

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # tiling_type, edge_length, gap, ratio_type, edge_ratio
        layout.prop(self, "tiling_type")
        layout.prop(self, "edge_length")
        layout.prop(self, "gap")
        column = layout.column(align=False)
        column.prop(self, "ratio_type")
        column.enabled = self.__is_enable_edge_ratio()
        column = layout.column(align=False)
        column.prop(self, "ratio_target")
        column.enabled = self.tiling_type == "3.4.6.4" and self.ratio_type != "distance"
        column = layout.column(align=False)
        column.prop(self, "ratio")
        column.enabled = self.__is_enable_input_edge_ratio()

        # start_x, end_x, step_x, start_y, end_y, step_y
        column = layout.column(align=True)        
        column.prop(self, "start_x")
        column.prop(self, "end_x")
        column.prop(self, "step_x")
        column = layout.column(align=True)
        column.prop(self, "start_y")        
        column.prop(self, "end_y")
        column.prop(self, "step_y")

        layout.prop(self, "uv")

        layout.prop(self, 'align')
        layout.prop(self, 'location')
        layout.prop(self, 'rotation')

    def execute(self, context):    
        # cache
        tiling_type = self.tiling_type
        edge_length = self.edge_length
        gap = self.gap
        ratio_type = self.ratio_type
        ratio_target = self.ratio_target
        ratio = self.ratio
        range_x = (self.start_x, self.end_x, self.step_x)
        range_y = (self.start_y, self.end_y, self.step_y)
        uv = self.uv
        
        # create vertices and faces
        vertices, faces = UniformTilings.create(tiling_type, edge_length, gap, ratio_type, ratio_target, ratio, range_x, range_y)
        mesh = bpy.data.meshes.new(name='Tiled')
        mesh.from_pydata(vertices, [], faces)
        
        # create uv map
        if uv == True:
            min_x = 1.7976931348623157e+308
            max_x = 2.2250738585072014e-308
            min_y = 1.7976931348623157e+308
            max_y = 2.2250738585072014e-308
            for vertex in vertices:
                if vertex[0] < min_x:
                    min_x = vertex[0]
                if vertex[0] > max_x:
                    max_x = vertex[0]
                if vertex[1] < min_y:
                    min_y = vertex[1]
                if vertex[1] > max_y:
                    max_y = vertex[1]
            width = max_x - min_x
            height = max_y - min_y
            size = width if width > height else height     
            mesh.uv_layers.new()
            for i, uvloop in enumerate(mesh.uv_layers.active.data):
                u = (vertices[i][0] - min_x) / size
                v = (vertices[i][1] - min_y) / size
                uvloop.uv = (u, v)
        
        object_data_add(context, mesh, operator=self)
        return {'FINISHED'} 

def menu_register_func(cls, context):
    cls.layout.separator()
    cls.layout.operator(OBJECT_OT_tile_regular_polygons.bl_idname, icon='PLUGIN')

classes = [
    OBJECT_OT_tile_regular_polygons,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_register_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_register_func)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
