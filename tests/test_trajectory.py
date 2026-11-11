"""trajectory 模块的单元测试。"""

import unittest

from embodied_utils.trajectory import (
    moving_average,
    path_length,
    resample_by_step,
    total_displacement,
)


class TrajectoryTestCase(unittest.TestCase):
    """轨迹处理函数的行为验证。"""

    def setUp(self):
        """准备一条沿 x 轴从 0 走到 2 的直线轨迹。"""
        self.straight = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]

    def test_path_length(self):
        """路径长度应等于相邻航点距离之和。"""
        self.assertAlmostEqual(path_length(self.straight), 2.0)
        self.assertAlmostEqual(path_length([]), 0.0)
        self.assertAlmostEqual(path_length([(1.0, 1.0)]), 0.0)

    def test_total_displacement(self):
        """净位移为首末航点之间的直线距离。"""
        self.assertAlmostEqual(total_displacement(self.straight), 2.0)
        self.assertAlmostEqual(total_displacement([]), 0.0)

    def test_resample_by_step(self):
        """重采样应按步长插入航点，并保留原始起终点。"""
        result = resample_by_step(self.straight, 0.5)
        self.assertEqual(len(result), 5)
        self.assertAlmostEqual(result[0][0], 0.0)
        self.assertAlmostEqual(result[-1][0], 2.0)

    def test_resample_skips_duplicate_points(self):
        """重合航点无法插值，应被跳过且不抛异常。"""
        result = resample_by_step([(0.0, 0.0), (0.0, 0.0), (1.0, 0.0)], 0.5)
        self.assertAlmostEqual(result[-1][0], 1.0)

    def test_resample_invalid_step(self):
        """非正步长应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            resample_by_step(self.straight, 0)

    def test_moving_average_keeps_length(self):
        """平滑后航点数量应与输入一致。"""
        result = moving_average(self.straight, 3)
        self.assertEqual(len(result), len(self.straight))
        # 中间点取邻域均值后仍为 1.0
        self.assertAlmostEqual(result[1][0], 1.0)

    def test_moving_average_window_one(self):
        """窗口为 1 时不平滑，航点保持原值。"""
        result = moving_average(self.straight, 1)
        self.assertEqual(result, [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])

    def test_moving_average_invalid_window(self):
        """小于 1 的窗口应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            moving_average(self.straight, 0)

    def test_invalid_trajectory(self):
        """None 轨迹应抛出 ValueError。"""
        with self.assertRaises(ValueError):
            path_length(None)


if __name__ == "__main__":
    unittest.main()
