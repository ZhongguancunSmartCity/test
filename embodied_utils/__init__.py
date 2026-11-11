"""具身智能轨迹处理工具包。

本包提供一组轻量、零第三方依赖的几何与轨迹处理函数，
用于机器人导航路径、航点平滑等场景的快速验证与单元测试。

所有源码均采用 UTF-8 编码，注释与文档字符串统一使用中文。
"""

from embodied_utils.geometry import (
    cross,
    distance,
    dot,
    lerp,
    normalize,
    vector_angle,
)
from embodied_utils.safety import (
    first_collision_index,
    is_collision,
    min_clearance,
    point_to_segment_distance,
)
from embodied_utils.trajectory import (
    moving_average,
    path_length,
    resample_by_step,
    total_displacement,
)

__version__ = "0.1.0"

__all__ = [
    "cross",
    "distance",
    "dot",
    "lerp",
    "normalize",
    "vector_angle",
    "first_collision_index",
    "is_collision",
    "min_clearance",
    "point_to_segment_distance",
    "moving_average",
    "path_length",
    "resample_by_step",
    "total_displacement",
]
