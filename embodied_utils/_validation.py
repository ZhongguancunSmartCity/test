"""包内共用的入参校验工具。

该模块仅供包内其他功能模块复用，不作为对外公开的 API 使用。
抽取公共校验逻辑的目的是让各模块对外抛出的异常类型与提示信息保持一致，
避免同一个错误在不同模块中出现不同的表现形式。
"""

from typing import List, Sequence, Tuple

Point = Sequence[float]
Trajectory = Sequence[Point]


def as_point(point: Point) -> Tuple[float, float]:
    """校验并拆分二维坐标，统一转换为 float。

    :param point: 待校验的坐标序列
    :return: 转换后的 ``(x, y)`` 元组
    :raises ValueError: 维度不是 2 或包含非数值元素时抛出
    """
    if point is None:
        raise ValueError("坐标不能为 None")
    if len(point) != 2:
        raise ValueError(
            "坐标必须包含且仅包含 2 个分量，实际得到 {0} 个".format(len(point))
        )
    try:
        return (float(point[0]), float(point[1]))
    except (TypeError, ValueError):
        raise ValueError("坐标分量必须是数值类型")


def as_trajectory(trajectory: Trajectory) -> List[Point]:
    """校验轨迹输入，返回可索引的航点列表。

    :param trajectory: 待校验的轨迹航点序列
    :return: 校验通过的航点列表
    :raises ValueError: 轨迹为 None 或某个航点不是二维坐标时抛出
    """
    if trajectory is None:
        raise ValueError("轨迹不能为 None")
    points = list(trajectory)
    for point in points:
        if point is None or len(point) != 2:
            raise ValueError("每个航点必须是包含 2 个分量的坐标")
    return points
