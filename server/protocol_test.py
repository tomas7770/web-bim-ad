import unittest
import uuid as uuidGen
import protocol

class TestProtocol(unittest.TestCase):

    def test_level_int_elevation(self):
        self.assertEqual(protocol.level(0, 0), "LEVEL 0 0")

    def test_level_float_elevation(self):
        self.assertEqual(protocol.level(0, 1.5), "LEVEL 0 1.5")

    def test_level_name(self):
        self.assertEqual(protocol.level(1, 0, "Custom Level"), "LEVEL 1 0 12:Custom Level")


    def test_optional_args_empty(self):
        self.assertEqual(protocol.optionalArgs(), "")

    def test_optional_args_zero(self):
        self.assertEqual(protocol.optionalArgs(0), " 0")

    def test_optional_args_multiple(self):
        self.assertEqual(protocol.optionalArgs(0, 1.0, protocol.string("some text")), " 0 1.0 9:some text")

    def test_optional_args_skip(self):
        self.assertEqual(protocol.optionalArgs(None, 1.0), " _ 1.0")

    def test_optional_args_skip_middle(self):
        self.assertEqual(protocol.optionalArgs(0, None, protocol.string("some text")), " 0 _ 9:some text")


class TestWallType(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.material_uuid = uuidGen.uuid1()

    def test_wall_type_empty(self):
        self.assertEqual(protocol.wallType(self.uuid), f"WALLTYPE {self.uuid}")

    def test_wall_type_thickness(self):
        self.assertEqual(protocol.wallType(self.uuid, thickness = 0.5), f"WALLTYPE {self.uuid} 0.5")

    def test_wall_type_material(self):
        self.assertEqual(protocol.wallType(self.uuid, material = self.material_uuid),
                         f"WALLTYPE {self.uuid} _ {self.material_uuid}")

    def test_wall_type_name(self):
        self.assertEqual(protocol.wallType(self.uuid, name = "Exterior Wall"), f"WALLTYPE {self.uuid} _ _ 13:Exterior Wall")

    def test_wall_type_full(self):
        self.assertEqual(protocol.wallType(self.uuid, 1, self.material_uuid, "Exterior Wall"),
                         f"WALLTYPE {self.uuid} 1 {self.material_uuid} 13:Exterior Wall")


class TestWall(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.type_uuid = uuidGen.uuid1()
        self.copy_uuid = uuidGen.uuid1()

    def test_wall_two_points(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5.5, 0)], 0), f"WALL {self.uuid} 2 0 0 5.5 0 0")

    def test_wall_three_points(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0), (7, 7)], 1), f"WALL {self.uuid} 3 0 0 5 0 7 7 1")

    def test_wall_with_type(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0)], 1, wallType = self.type_uuid),
                         f"WALL {self.uuid} 2 0 0 5 0 1 {self.type_uuid}")

    def test_wall_top_level(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0)], 1, topLevel = 3),
                         f"WALL {self.uuid} 2 0 0 5 0 1 _ 3")

    def test_wall_height(self):
            self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0)], 1, height = 3.5),
                             f"WALL {self.uuid} 2 0 0 5 0 1 _ _ 3.5")

    def test_wall_full(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0)], 1, wallType = self.type_uuid, topLevel = 3, height = 3.5),
                         f"WALL {self.uuid} 2 0 0 5 0 1 {self.type_uuid} 3 3.5")

    def test_wall_copy_uuid(self):
        self.assertEqual(protocol.wall(self.uuid, [(0, 0), (5, 0)], 1, copyUuid = self.copy_uuid),
                         f"WALL {self.uuid} 2 0 0 5 0 1 _ _ _ {self.copy_uuid}")

    def test_wall_fail_one_point(self):
        with self.assertRaises(AssertionError):
            protocol.wall(self.uuid, [(0, 0)], 0)


class TestSlabType(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.material_uuid = uuidGen.uuid1()

    def test_slab_type_empty(self):
        self.assertEqual(protocol.slabType(self.uuid), f"SLABTYPE {self.uuid}")

    def test_slab_type_thickness(self):
        self.assertEqual(protocol.slabType(self.uuid, thickness = 0.5), f"SLABTYPE {self.uuid} 0.5")

    def test_slab_type_material(self):
        self.assertEqual(protocol.slabType(self.uuid, material = self.material_uuid),
                         f"SLABTYPE {self.uuid} _ {self.material_uuid}")

    def test_slab_type_name(self):
        self.assertEqual(protocol.slabType(self.uuid, name = "Custom Slab"), f"SLABTYPE {self.uuid} _ _ 11:Custom Slab")

    def test_slab_type_full(self):
        self.assertEqual(protocol.slabType(self.uuid, 1, self.material_uuid, "Custom Slab"),
                         f"SLABTYPE {self.uuid} 1 {self.material_uuid} 11:Custom Slab")


class TestSlab(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.type_uuid = uuidGen.uuid1()

    def test_slab_three_points(self):
        self.assertEqual(protocol.slab(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], 0),
                         f"SLAB {self.uuid} 3 0 0 5 0 2.5 2.5 0")

    def test_slab_four_points(self):
        self.assertEqual(protocol.slab(self.uuid, [(0, 0), (5, 0), (5, 5), (0, 5)], 0),
                         f"SLAB {self.uuid} 4 0 0 5 0 5 5 0 5 0")

    def test_slab_with_type(self):
        self.assertEqual(protocol.slab(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], 1, slabType = self.type_uuid),
                         f"SLAB {self.uuid} 3 0 0 5 0 2.5 2.5 1 {self.type_uuid}")

    def test_slab_fail_two_points(self):
        with self.assertRaises(AssertionError):
            protocol.slab(self.uuid, [(0, 0), (5, 0)], 0)


    def test_slab_rect_basic(self):
        self.assertEqual(protocol.slabRect(self.uuid, {"start": (0, 1), "end": (2, 3.5)}, 0),
                         f"SLABRECT {self.uuid} 0 1 2 3.5 0")

    def test_slab_rect_with_type(self):
        self.assertEqual(protocol.slabRect(self.uuid, {"start": (0, 1), "end": (2, 3)}, 1, slabType = self.type_uuid),
                         f"SLABRECT {self.uuid} 0 1 2 3 1 {self.type_uuid}")


class TestRoof(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.type_uuid = uuidGen.uuid1()

    def test_roof_three_points(self):
        self.assertEqual(protocol.roof(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], 0),
                         f"ROOF {self.uuid} 3 0 0 5 0 2.5 2.5 0")

    def test_roof_four_points(self):
        self.assertEqual(protocol.roof(self.uuid, [(0, 0), (5, 0), (5, 5), (0, 5)], 0),
                         f"ROOF {self.uuid} 4 0 0 5 0 5 5 0 5 0")

    def test_roof_with_type(self):
        self.assertEqual(protocol.roof(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], 1, roofType = self.type_uuid),
                         f"ROOF {self.uuid} 3 0 0 5 0 2.5 2.5 1 {self.type_uuid}")

    def test_roof_fail_two_points(self):
        with self.assertRaises(AssertionError):
            protocol.roof(self.uuid, [(0, 0), (5, 0)], 0)


class TestBeamType(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.material_uuid = uuidGen.uuid1()

    def test_beam_type_empty(self):
        self.assertEqual(protocol.beamType(self.uuid), f"BEAMTYPE {self.uuid}")

    def test_beam_type_three_points_profile(self):
        self.assertEqual(protocol.beamType(self.uuid, profile = [(0, 0), (5, 0), (2.5, 2.5)]),
                         f"BEAMTYPE {self.uuid} 3 0 0 5 0 2.5 2.5")

    def test_beam_type_four_points_profile(self):
        self.assertEqual(protocol.beamType(self.uuid, profile = [(0, 0), (5, 0), (5, 5), (0, 5)]),
                         f"BEAMTYPE {self.uuid} 4 0 0 5 0 5 5 0 5")

    def test_beam_type_material(self):
        self.assertEqual(protocol.beamType(self.uuid, material = self.material_uuid),
                         f"BEAMTYPE {self.uuid} _ {self.material_uuid}")

    def test_beam_type_name(self):
        self.assertEqual(protocol.beamType(self.uuid, name = "Custom Beam"),
                         f"BEAMTYPE {self.uuid} _ _ 11:Custom Beam")

    def test_beam_type_full(self):
        self.assertEqual(protocol.beamType(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], self.material_uuid, "Custom Beam"),
                         f"BEAMTYPE {self.uuid} 3 0 0 5 0 2.5 2.5 {self.material_uuid} 11:Custom Beam")

    def test_beam_type_fail_two_points_profile(self):
        with self.assertRaises(AssertionError):
            protocol.beamType(self.uuid, [(0, 0), (5, 0)])


class TestBeam(unittest.TestCase):

    def setUp(self):
        self.type_uuid = uuidGen.uuid1()

    def test_beam_no_type(self):
        self.assertEqual(protocol.beam([(1, 2), (3, 3.5)], 0), f"BEAM 1 2 3 3.5 0")

    def test_beam_with_type(self):
        self.assertEqual(protocol.beam([(1, 2), (3, 3.5)], 1, beamType = self.type_uuid),
                         f"BEAM 1 2 3 3.5 1 _ {self.type_uuid}")

    def test_beam_elevation(self):
        self.assertEqual(protocol.beam([(1, 2), (3, 3.5)], 1, elevation = 2.5),
                         f"BEAM 1 2 3 3.5 1 2.5")

    def test_beam_full(self):
        self.assertEqual(protocol.beam([(1, 2), (3, 3.5)], 1, beamType = self.type_uuid, elevation = 2.5),
                         f"BEAM 1 2 3 3.5 1 2.5 {self.type_uuid}")

    def test_beam_fail_one_point(self):
        with self.assertRaises(AssertionError):
            protocol.beam([(1, 2)], 0)

    def test_beam_fail_three_points(self):
        with self.assertRaises(AssertionError):
            protocol.beam([(1, 2), (3, 3.5), (4, 5)], 0)


class TestColumnType(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.material_uuid = uuidGen.uuid1()

    def test_column_type_empty(self):
        self.assertEqual(protocol.columnType(self.uuid), f"COLUMNTYPE {self.uuid}")

    def test_column_type_three_points_profile(self):
        self.assertEqual(protocol.columnType(self.uuid, profile = [(0, 0), (5, 0), (2.5, 2.5)]),
                         f"COLUMNTYPE {self.uuid} 3 0 0 5 0 2.5 2.5")

    def test_column_type_four_points_profile(self):
        self.assertEqual(protocol.columnType(self.uuid, profile = [(0, 0), (5, 0), (5, 5), (0, 5)]),
                         f"COLUMNTYPE {self.uuid} 4 0 0 5 0 5 5 0 5")

    def test_column_type_material(self):
        self.assertEqual(protocol.columnType(self.uuid, material = self.material_uuid),
                         f"COLUMNTYPE {self.uuid} _ {self.material_uuid}")

    def test_column_type_name(self):
        self.assertEqual(protocol.columnType(self.uuid, name = "Custom Column"),
                         f"COLUMNTYPE {self.uuid} _ _ 13:Custom Column")

    def test_column_type_full(self):
        self.assertEqual(protocol.columnType(self.uuid, [(0, 0), (5, 0), (2.5, 2.5)], self.material_uuid, "Custom Column"),
                         f"COLUMNTYPE {self.uuid} 3 0 0 5 0 2.5 2.5 {self.material_uuid} 13:Custom Column")

    def test_column_type_fail_two_points_profile(self):
        with self.assertRaises(AssertionError):
            protocol.columnType(self.uuid, [(0, 0), (5, 0)])


class TestColumn(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.type_uuid = uuidGen.uuid1()
        self.copy_uuid = uuidGen.uuid1()

    def test_column_no_type(self):
        self.assertEqual(protocol.column(self.uuid, (3, 3.5), 0), f"COLUMN {self.uuid} 3 3.5 0")

    def test_column_with_type(self):
        self.assertEqual(protocol.column(self.uuid, (1, 2), 1, columnType = self.type_uuid),
                         f"COLUMN {self.uuid} 1 2 1 {self.type_uuid}")

    def test_column_top_position(self):
            self.assertEqual(protocol.column(self.uuid, (1, 2), 1, topPosition = (3, 4)),
                             f"COLUMN {self.uuid} 1 2 1 _ 3 4")

    def test_column_angle(self):
            self.assertEqual(protocol.column(self.uuid, (1, 2), 1, angle = 45.4),
                             f"COLUMN {self.uuid} 1 2 1 _ _ _ 45.4")

    def test_column_top_level(self):
        self.assertEqual(protocol.column(self.uuid, (1, 2), 1, topLevel = 3),
                         f"COLUMN {self.uuid} 1 2 1 _ _ _ _ 3")

    def test_column_full(self):
        self.assertEqual(protocol.column(self.uuid, (1, 2), 1, columnType = self.type_uuid, topPosition = (3, 4),
                                         angle = 60, topLevel = 3),
                         f"COLUMN {self.uuid} 1 2 1 {self.type_uuid} 3 4 60 3")

    def test_column_copy_uuid(self):
        self.assertEqual(protocol.column(self.uuid, (1, 2), 1, copyUuid = self.copy_uuid),
                         f"COLUMN {self.uuid} 1 2 1 _ _ _ _ _ {self.copy_uuid}")


class TestMaterial(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()

    def test_material_empty(self):
        self.assertEqual(protocol.material(self.uuid), f"MATERIAL {self.uuid}")

    def test_material_albedo(self):
        self.assertEqual(protocol.material(self.uuid, albedo = (1.0, 0.5, 0)), f"MATERIAL {self.uuid} 1.0,0.5,0")

    def test_material_opacity(self):
        self.assertEqual(protocol.material(self.uuid, opacity = 0.25), f"MATERIAL {self.uuid} _ 0.25")

    def test_material_texture(self):
        self.assertEqual(protocol.material(self.uuid, texturePath = "./uvGrid2.jpg"),
                         f"MATERIAL {self.uuid} _ _ _ _ 13:./uvGrid2.jpg")

    def test_material_texture_spaces(self):
        self.assertEqual(protocol.material(self.uuid, texturePath = "./My texture.jpg"),
                         f"MATERIAL {self.uuid} _ _ _ _ 16:./My texture.jpg")

    def test_material_texture_x_scale(self):
        self.assertEqual(protocol.material(self.uuid, texturePath = "./uvGrid2.jpg", xScale = 2),
                         f"MATERIAL {self.uuid} _ _ 2 _ 13:./uvGrid2.jpg")

    def test_material_texture_y_scale(self):
        self.assertEqual(protocol.material(self.uuid, texturePath = "./uvGrid2.jpg", yScale = 1.5),
                         f"MATERIAL {self.uuid} _ _ _ 1.5 13:./uvGrid2.jpg")

    def test_material_texture_xy_scale(self):
        self.assertEqual(protocol.material(self.uuid, texturePath = "./uvGrid2.jpg", xScale = 2, yScale = 1.5),
                         f"MATERIAL {self.uuid} _ _ 2 1.5 13:./uvGrid2.jpg")

    def test_material_name(self):
        self.assertEqual(protocol.material(self.uuid, name = "My Material"), f"MATERIAL {self.uuid} _ _ _ _ _ 11:My Material")

    def test_material_full(self):
        self.assertEqual(protocol.material(self.uuid, albedo = (1.0, 0.5, 0), opacity = 0.5,
                                           texturePath = "./uvGrid2.jpg", xScale = 2, yScale = 1.5, name = "My Material"),
                         f"MATERIAL {self.uuid} 1.0,0.5,0 0.5 2 1.5 13:./uvGrid2.jpg 11:My Material")

    def test_material_fail_albedo_len_2(self):
        with self.assertRaises(AssertionError):
            protocol.material(self.uuid, albedo = (1.0, 0.5))

    def test_material_fail_albedo_len_4(self):
        with self.assertRaises(AssertionError):
            protocol.material(self.uuid, albedo = (1.0, 0.5, 0, 0.123))


class TestOpening(unittest.TestCase):

    def setUp(self):
        self.host_uuid = uuidGen.uuid1()

    def test_opening_int_values(self):
        self.assertEqual(protocol.opening(self.host_uuid, 0, 1, 2, 3),
                         f"OPENING {self.host_uuid} 0 1 2 3")

    def test_opening_float_values(self):
        self.assertEqual(protocol.opening(self.host_uuid, 1.0, 1.5, 2.34, 3.456),
                         f"OPENING {self.host_uuid} 1.0 1.5 2.34 3.456")

    def test_opening_poly_three_points(self):
        self.assertEqual(protocol.openingPoly(self.host_uuid, [(0, 0), (5, 0), (2.5, 2.5)]),
                                 f"OPENINGPOLY {self.host_uuid} 3 0 0 5 0 2.5 2.5")

    def test_opening_poly_four_points(self):
            self.assertEqual(protocol.openingPoly(self.host_uuid, [(0, 0), (5, 0), (5, 5), (0, 5)]),
                                     f"OPENINGPOLY {self.host_uuid} 4 0 0 5 0 5 5 0 5")

    def test_opening_poly_fail_two_points(self):
            with self.assertRaises(AssertionError):
                protocol.openingPoly(self.host_uuid, [(0, 0), (5, 0)])


class TestStairType(unittest.TestCase):

    def setUp(self):
        self.uuid = uuidGen.uuid1()
        self.material_uuid = uuidGen.uuid1()

    def test_stair_type_empty(self):
        self.assertEqual(protocol.stairType(self.uuid), f"STAIRTYPE {self.uuid}")

    def test_stair_type_width(self):
        self.assertEqual(protocol.stairType(self.uuid, width = 1.5), f"STAIRTYPE {self.uuid} 1.5")

    def test_stair_type_height(self):
        self.assertEqual(protocol.stairType(self.uuid, height = 0.15), f"STAIRTYPE {self.uuid} _ 0.15")

    def test_stair_type_depth(self):
        self.assertEqual(protocol.stairType(self.uuid, depth = 0.3), f"STAIRTYPE {self.uuid} _ _ 0.3")

    def test_stair_type_material(self):
        self.assertEqual(protocol.stairType(self.uuid, material = self.material_uuid),
                         f"STAIRTYPE {self.uuid} _ _ _ {self.material_uuid}")

    def test_stair_type_name(self):
        self.assertEqual(protocol.stairType(self.uuid, name = "Custom Stair"),
                         f"STAIRTYPE {self.uuid} _ _ _ _ 12:Custom Stair")

    def test_stair_type_full(self):
        self.assertEqual(protocol.stairType(self.uuid, 1, 0.18, 0.28, self.material_uuid, "Custom Stair"),
                         f"STAIRTYPE {self.uuid} 1 0.18 0.28 {self.material_uuid} 12:Custom Stair")


class TestStair(unittest.TestCase):

    def setUp(self):
        self.type_uuid = uuidGen.uuid1()

    def test_stair_no_type(self):
        self.assertEqual(protocol.stair((3, 3.5), (1, 0), 2), f"STAIR 3 3.5 1 0 2")

    def test_stair_with_type(self):
        self.assertEqual(protocol.stair((1, 2), (0, 1), 1, stairType = self.type_uuid),
                         f"STAIR 1 2 0 1 1 {self.type_uuid}")

    def test_stair_top_level(self):
        self.assertEqual(protocol.stair((1, 2), (1, 1), 2, topLevel = 3),
                         f"STAIR 1 2 1 1 2 _ 3")

    def test_stair_full(self):
        self.assertEqual(protocol.stair((1, 2), (1, 0), 1, stairType = self.type_uuid, topLevel = 3),
                         f"STAIR 1 2 1 0 1 {self.type_uuid} 3")

if __name__ == '__main__':
    unittest.main()
