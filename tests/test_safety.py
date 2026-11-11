"""safety 模块的单元测试。"""

import unittest

from embodied_utils.safety import (
    first_collision_index,
    is_collision,
    min_clearance,
    point_to_segment_distance,
)


class SafetyTestCase(unittest.TestCase):
    """安全性检查函数的行为验证。"""

    def test_point_to_segment_distance(self):
        """投影落在线段内部时，距离为垂足距离。"""
        self.assertAlmostEqual(
            point_to_segment_distance((1, 1), (0, 0), (2, 0)), 1.0
        )

    def test_point_to_segment_distance_clamped_to_endpoint(self):
        """投影落在延长线上时，距离取到最近端点的距离。"""
        self.assertAlmostEqual(
            point_to_segment_distance((3, 0), (0, 0), (2, 0)), 1.0
        )

    def test_point_to_degenerate_segment(self):
        """起终点重合的退化线段，距离即点到该点的距离。"""
        self.assertAlmostEqual(
            point_to_segment_distance((3, 4), (0, 0), (0, 0)), 5.0
        )

    def test_is_collision(self):
        """圆心距小于或等于半径时判定为碰撞。"""
        self.assertTrue(is_collision((0, 0), (1, 0, 1.0)))
        self.assertFalse(is_collision((0, 0), (3, 0, 1.0)))

    def test_is_collision_with_invalid_obstacle(self):
        """障碍物格式非法时抛出 ValueError。"""
        with self.assertRaises(ValueError):
            is_collision((0, 0), (1, 0))

    def test_is_collision_with_negative_radius(self):
        """障碍物半径为负时抛出 ValueError。"""
        with self.assertRaises(ValueError):
            is_collision((0, 0), (1, 0, -1.0))

    def test_first_collision_index(self):
        """应返回首个与障碍物冲突的航点下标。"""
        trajectory = [(0, 0), (5, 0), (10, 0)]
        self.assertEqual(first_collision_index(trajectory, [(5, 0, 0.5)]), 1)

    def test_first_collision_index_none(self):
        """全程无碰撞时返回 None。"""
        trajectory = [(0, 0), (5, 0)]
        self.assertIsNone(first_collision_index(trajectory, [(50, 50, 1.0)]))

    def test_first_collision_between_waypoints(self):
        """航点之间的连线穿过障碍物时，同样应判定为碰撞。"""
        trajectory = [(0, 0), (10, 0)]
        self.assertEqual(first_collision_index(trajectory, [(5, 0, 0.5)]), 1)

    def test_first_collision_with_robot_radius(self):
        """机器人半径应计入碰撞判定阈值。"""
        trajectory = [(0, 0), (10, 0)]
        obstacles = [(5, 1.5, 0.5)]
        # 质点形态下障碍物在安全距离之外
        self.assertIsNone(first_collision_index(trajectory, obstacles, robot_radius=0.0))
        # 计入机器人半径后判定为碰撞
        self.assertEqual(
            first_collision_index(trajectory, obstacles, robot_radius=1.0), 1
        )

    def test_first_collision_with_negative_robot_radius(self):
        """机器人半径为负时抛出 ValueError。"""
        with self.assertRaises(ValueError):
            first_collision_index([(0, 0)], [], robot_radius=-0.5)

    def test_min_clearance(self):
        """最小间隙应为轨迹到障碍物表面的最短距离。"""
        trajectory = [(0, 0), (5, 0)]
        self.assertAlmostEqual(min_clearance(trajectory, [(10, 0, 1.0)]), 4.0)

    def test_min_clearance_without_obstacles(self):
        """障碍物列表为空时返回正无穷。"""
        self.assertEqual(min_clearance([(0, 0)], []), float("inf"))

    def test_invalid_trajectory(self):
        """None 轨迹应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            first_collision_index(None, [(0, 0, 1.0)])


if __name__ == "__main__":
    unittest.main()
