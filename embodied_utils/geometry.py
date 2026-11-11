"""二维几何基础工具函数。

所有函数均接受形如 ``(x, y)`` 的二维序列，坐标既可以是 ``tuple``，
也可以是 ``list``。为保证行为可预期，函数在遇到非法入参时统一抛出
``ValueError``，而不是静默返回错误结果。
"""

import math
from typing import Sequence, Tuple

from embodied_utils._validation import as_point

Point = Sequence[float]
Vector = Sequence[float]


def distance(p1: Point, p2: Point) -> float:
    """计算两个二维点之间的欧氏距离。

    :param p1: 起点，坐标序列 ``(x, y)``
    :param p2: 终点，坐标序列 ``(x, y)``
    :return: 两点间的欧氏距离，恒为非负数
    :raises ValueError: 当任意一点不是二维坐标时抛出
    """
    x1, y1 = as_point(p1)
    x2, y2 = as_point(p2)
    return math.hypot(x2 - x1, y2 - y1)


def normalize(vector: Vector) -> Tuple[float, float]:
    """将向量单位化。

    零向量无法确定方向，此时直接返回 ``(0.0, 0.0)``，
    避免出现除零异常。

    :param vector: 待单位化的二维向量
    :return: 与入参同方向的单位向量
    :raises ValueError: 当入参不是二维坐标时抛出
    """
    x, y = as_point(vector)
    norm = math.hypot(x, y)
    if norm == 0.0:
        return (0.0, 0.0)
    return (x / norm, y / norm)


def dot(u: Vector, v: Vector) -> float:
    """计算两个二维向量的点积。

    :param u: 第一个向量
    :param v: 第二个向量
    :return: 点积标量值
    :raises ValueError: 当任一向量不是二维坐标时抛出
    """
    ux, uy = as_point(u)
    vx, vy = as_point(v)
    return ux * vx + uy * vy


def cross(u: Vector, v: Vector) -> float:
    """计算两个二维向量的叉积标量值（z 分量）。

    :param u: 第一个向量
    :param v: 第二个向量
    :return: 叉积的 z 分量，正值表示 v 相对 u 逆时针旋转
    :raises ValueError: 当任一向量不是二维坐标时抛出
    """
    ux, uy = as_point(u)
    vx, vy = as_point(v)
    return ux * vy - uy * vx


def lerp(a: Point, b: Point, t: float) -> Tuple[float, float]:
    """在两点之间做线性插值。

    ``t`` 取值超出 ``[0, 1]`` 时同样有效，此时相当于沿直线方向外插。

    :param a: 起点坐标
    :param b: 终点坐标
    :param t: 插值比例，0 表示起点，1 表示终点
    :return: 插值得到的坐标
    :raises ValueError: 当任一坐标不是二维坐标时抛出
    """
    ax, ay = as_point(a)
    bx, by = as_point(b)
    return (ax + (bx - ax) * t, ay + (by - ay) * t)


def vector_angle(u: Vector, v: Vector) -> float:
    """计算两个向量之间的夹角，单位为弧度，取值范围 ``[0, pi]``。

    任一向量为零向量时夹角无定义，此时返回 ``0.0``。

    :param u: 第一个向量
    :param v: 第二个向量
    :return: 两向量夹角，单位弧度
    :raises ValueError: 当任一向量不是二维坐标时抛出
    """
    ux, uy = as_point(u)
    vx, vy = as_point(v)
    norm_u = math.hypot(ux, uy)
    norm_v = math.hypot(vx, vy)
    if norm_u == 0.0 or norm_v == 0.0:
        return 0.0
    # 先夹逼余弦值再取反余弦，避免浮点误差导致 acos 入参越界
    cos_theta = (ux * vx + uy * vy) / (norm_u * norm_v)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.acos(cos_theta)
