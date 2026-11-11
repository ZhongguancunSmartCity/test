"""geometry 模块的单元测试。"""

import math
import unittest

from embodied_utils.geometry import (
    cross,
    distance,
    dot,
    lerp,
    normalize,
    vector_angle,
)


class GeometryTestCase(unittest.TestCase):
    """二维几何函数的行为验证。"""

    def test_distance(self):
        """欧氏距离应符合勾股定理结果。"""
        self.assertAlmostEqual(distance((0, 0), (3, 4)), 5.0)
        self.assertAlmostEqual(distance((1, 1), (1, 1)), 0.0)

    def test_distance_with_invalid_point(self):
        """维度不是 2 的坐标应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            distance((0, 0), (1, 2, 3))

    def test_normalize(self):
        """归一化后向量模长应为 1。"""
        self.assertEqual(normalize((3, 4)), (0.6, 0.8))

    def test_normalize_zero_vector(self):
        """零向量方向未定义，归一化后保持零向量且不抛异常。"""
        self.assertEqual(normalize((0, 0)), (0.0, 0.0))

    def test_dot_and_cross(self):
        """点积与叉积应符合定义。"""
        self.assertAlmostEqual(dot((1, 2), (3, 4)), 11.0)
        self.assertAlmostEqual(cross((1, 0), (0, 1)), 1.0)

    def test_lerp(self):
        """插值结果应落在两端点连线上。"""
        self.assertEqual(lerp((0, 0), (10, 20), 0.5), (5.0, 10.0))
        # t 超出 [0, 1] 时沿直线外插
        self.assertEqual(lerp((0, 0), (10, 0), 2.0), (20.0, 0.0))

    def test_vector_angle(self):
        """夹角计算应返回 [0, pi] 区间内的弧度值。"""
        self.assertAlmostEqual(vector_angle((1, 0), (0, 1)), math.pi / 2)
        self.assertAlmostEqual(vector_angle((1, 0), (1, 0)), 0.0)
        # 零向量夹角无定义，返回 0
        self.assertEqual(vector_angle((0, 0), (1, 0)), 0.0)


if __name__ == "__main__":
    unittest.main()
