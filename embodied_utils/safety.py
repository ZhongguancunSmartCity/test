"""轨迹安全性检查与碰撞检测工具。

机器人在平面环境中运动时，可借助本模块判断：

1. 给定轨迹是否会与障碍物发生碰撞，以及首次碰撞出现在哪个航点；
2. 轨迹与障碍物之间还剩多少安全间隙。

障碍物统一用圆形描述，格式为 ``(x, y, radius)``；机器人自身也按
带半径的圆形足迹处理。所有距离单位与输入坐标保持一致，不做单位换算。
"""

import math
from typing import List, Optional, Sequence, Tuple

from embodied_utils._validation import as_point, as_trajectory

Point = Sequence[float]
Obstacle = Sequence[float]
Trajectory = Sequence[Point]


def point_to_segment_distance(
    point: Point, seg_start: Point, seg_end: Point
) -> float:
    """计算点到线段的最短距离。

    采用投影法：先把点投影到线段所在的直线上，再根据投影参数是否落在
    ``[0, 1]`` 区间决定取垂足还是取最近端点。与"点到直线距离"的区别
    在于，本函数在投影落到延长线上时返回的是到最近端点的距离。

    :param point: 待求距离的坐标
    :param seg_start: 线段起点坐标
    :param seg_end: 线段终点坐标
    :return: 点到线段的最短距离，恒为非负数
    :raises ValueError: 当任一坐标不是二维坐标时抛出
    """
    px, py = as_point(point)
    ax, ay = as_point(seg_start)
    bx, by = as_point(seg_end)
    dx = bx - ax
    dy = by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        # 起终点重合的退化线段，距离即为点到该点的距离
        return math.hypot(px - ax, py - ay)
    projection = ((px - ax) * dx + (py - ay) * dy) / length_sq
    # 投影参数需夹逼到 [0, 1]，否则应取最近端点而非垂足
    projection = max(0.0, min(1.0, projection))
    return math.hypot(px - (ax + projection * dx), py - (ay + projection * dy))


def is_collision(point: Point, obstacle: Obstacle) -> bool:
    """判断单个航点是否与单个障碍物发生碰撞。

    :param point: 航点坐标
    :param obstacle: 障碍物，格式为 ``(x, y, radius)``
    :return: 两者圆心距小于或等于障碍物半径时返回 True
    :raises ValueError: 当坐标或障碍物格式非法时抛出
    """
    px, py = as_point(point)
    ox, oy, radius = as_obstacle(obstacle)
    return math.hypot(px - ox, py - oy) <= radius


def first_collision_index(
    trajectory: Trajectory,
    obstacles: Sequence[Obstacle],
    robot_radius: float = 0.0,
) -> Optional[int]:
    """返回轨迹中首次与障碍物发生碰撞的航点下标。

    机器人在相邻航点之间沿直线运动，因此除了检查航点本身，
    还要检查航点之间的连线段是否侵入障碍物范围。判定阈值为
    ``机器人半径 + 障碍物半径``。

    :param trajectory: 轨迹航点序列
    :param obstacles: 障碍物列表，每个元素格式为 ``(x, y, radius)``
    :param robot_radius: 机器人自身半径，默认 0 表示按质点处理
    :return: 首个受影响的航点下标，全程无碰撞时返回 None
    :raises ValueError: 当轨迹、障碍物或半径参数非法时抛出
    """
    points = as_trajectory(trajectory)
    if robot_radius < 0:
        raise ValueError("机器人半径不能为负数，实际得到 {0}".format(robot_radius))
    if len(points) == 0:
        return None

    for index in range(len(points)):
        for obstacle in obstacles:
            ox, oy, radius = as_obstacle(obstacle)
            limit = robot_radius + radius
            # 先判断航点本身是否已经落入障碍范围
            if math.hypot(points[index][0] - ox, points[index][1] - oy) <= limit:
                return index
            # 再判断与前一航点之间的连线段是否侵入障碍范围
            if index > 0:
                gap = point_to_segment_distance(
                    (ox, oy), points[index - 1], points[index]
                )
                if gap <= limit:
                    return index
    return None


def min_clearance(
    trajectory: Trajectory, obstacles: Sequence[Obstacle]
) -> float:
    """计算轨迹与所有障碍物之间的最小间隙。

    间隙定义为"轨迹到障碍物表面的最短距离"，为负值表示已经侵入
    障碍物内部，数值越小说明距离碰撞越近。

    :param trajectory: 轨迹航点序列
    :param obstacles: 障碍物列表，每个元素格式为 ``(x, y, radius)``
    :return: 最小间隙；障碍物列表为空时返回正无穷
    :raises ValueError: 当轨迹或障碍物格式非法时抛出
    """
    points = as_trajectory(trajectory)
    if not obstacles:
        return float("inf")

    minimum = float("inf")
    for index in range(len(points)):
        for obstacle in obstacles:
            ox, oy, radius = as_obstacle(obstacle)
            # 航点到障碍物圆心的距离减去半径，即该航点的间隙
            gap = math.hypot(points[index][0] - ox, points[index][1] - oy) - radius
            minimum = min(minimum, gap)
            if index > 0:
                # 连线段同样可能比航点更靠近障碍物
                segment_gap = point_to_segment_distance(
                    (ox, oy), points[index - 1], points[index]
                ) - radius
                minimum = min(minimum, segment_gap)
    return minimum


def as_obstacle(obstacle: Obstacle) -> Tuple[float, float, float]:
    """校验并拆分障碍物定义，统一转换为 float。

    :param obstacle: 障碍物，格式为 ``(x, y, radius)``
    :return: 转换后的 ``(x, y, radius)`` 元组
    :raises ValueError: 格式非法或半径为负时抛出
    """
    if obstacle is None:
        raise ValueError("障碍物不能为 None")
    if len(obstacle) != 3:
        raise ValueError(
            "障碍物必须包含且仅包含 3 个分量 (x, y, radius)，实际得到 {0} 个".format(
                len(obstacle)
            )
        )
    try:
        x = float(obstacle[0])
        y = float(obstacle[1])
        radius = float(obstacle[2])
    except (TypeError, ValueError):
        raise ValueError("障碍物分量必须是数值类型")
    if radius < 0:
        raise ValueError("障碍物半径不能为负数，实际得到 {0}".format(radius))
    return (x, y, radius)
