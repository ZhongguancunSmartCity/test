"""轨迹（航点序列）处理工具。

轨迹统一表示为按时间先后排列的二维航点序列，例如机器人导航过程中
逐帧记录的位置点。所有函数都对空轨迹和单点轨迹做了保护处理，
不会因为边界数据抛出非预期异常。
"""

from typing import List, Sequence, Tuple

from embodied_utils._validation import as_trajectory
from embodied_utils.geometry import distance, lerp

Point = Sequence[float]
Trajectory = Sequence[Point]


def path_length(trajectory: Trajectory) -> float:
    """计算轨迹总长度，即相邻航点之间距离的累加。

    空轨迹与单点轨迹的长度均为 ``0.0``。

    :param trajectory: 轨迹航点序列
    :return: 轨迹总长度
    :raises ValueError: 当轨迹为 None 或航点格式非法时抛出
    """
    points = as_trajectory(trajectory)
    total = 0.0
    for index in range(1, len(points)):
        total += distance(points[index - 1], points[index])
    return total


def total_displacement(trajectory: Trajectory) -> float:
    """计算轨迹首末航点之间的直线距离（净位移）。

    与 :func:`path_length` 不同，该值不反映路径的曲折程度。

    :param trajectory: 轨迹航点序列
    :return: 首末航点之间的欧氏距离
    :raises ValueError: 当轨迹为 None 或航点格式非法时抛出
    """
    points = as_trajectory(trajectory)
    if len(points) < 2:
        return 0.0
    return distance(points[0], points[-1])


def resample_by_step(
    trajectory: Trajectory, step: float
) -> List[Tuple[float, float]]:
    """按固定步长对轨迹重采样。

    沿轨迹每隔 ``step`` 的距离插入一个新航点，原始起点与终点始终保留。
    当相邻航点的间距小于 ``step`` 时，该段不做插值；若相邻航点完全重合，
    则直接跳过该段以避免除零。

    :param trajectory: 原始轨迹航点序列
    :param step: 采样步长，必须为正数
    :return: 重采样后的航点列表
    :raises ValueError: 当步长非正数，或轨迹格式非法时抛出
    """
    points = as_trajectory(trajectory)
    if step <= 0:
        raise ValueError("步长必须为正数，实际得到 {0}".format(step))
    if len(points) == 0:
        return []

    result = [(float(points[0][0]), float(points[0][1]))]
    for index in range(1, len(points)):
        start = points[index - 1]
        end = points[index]
        segment = distance(start, end)
        if segment == 0.0:
            # 重合航点无法插值，直接跳过，避免除零
            continue
        # 完整落入该段的插值点数量，最后一个插值点恰好落在终点上
        count = int(segment // step)
        for k in range(1, count + 1):
            ratio = k * step / segment
            result.append(lerp(start, end, ratio))

    last = (float(points[-1][0]), float(points[-1][1]))
    # 终点可能已由插值产生，仅在缺失时补齐
    if result[-1] != last:
        result.append(last)
    return result


def moving_average(
    trajectory: Trajectory, window: int
) -> List[Tuple[float, float]]:
    """对轨迹做滑动窗口平滑。

    使用窗口内航点的均值替换原始航点，窗口在轨迹两端自动收缩，
    因此输出长度与输入保持一致。``window`` 为 1 时不做任何处理。

    :param trajectory: 原始轨迹航点序列
    :param window: 滑动窗口大小，必须为正整数
    :return: 平滑后的航点列表，长度与输入一致
    :raises ValueError: 当窗口小于 1，或轨迹格式非法时抛出
    """
    points = as_trajectory(trajectory)
    if window < 1:
        raise ValueError("窗口大小必须为正整数，实际得到 {0}".format(window))
    if len(points) == 0:
        return []

    result: List[Tuple[float, float]] = []
    half = window // 2
    for index in range(len(points)):
        start = max(0, index - half)
        end = min(len(points), index + half + 1)
        window_points = points[start:end]
        avg_x = sum(float(p[0]) for p in window_points) / len(window_points)
        avg_y = sum(float(p[1]) for p in window_points) / len(window_points)
        result.append((avg_x, avg_y))
    return result
