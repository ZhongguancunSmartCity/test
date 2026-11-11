# embodied-utils

面向具身智能场景的轻量几何与轨迹处理工具集，同时作为 **GitHub 分支保护与 PR 合并流程** 的验证仓库使用。

## 功能特性

- 二维几何基础运算：欧氏距离、向量归一化、点积、叉积、线性插值、夹角计算
- 轨迹处理：路径长度、净位移、定步长重采样、滑动窗口平滑
- 安全性检查：点到线段距离、碰撞判定、首次碰撞下标、最小安全间隙
- 零第三方依赖，兼容 Python 3.8 及以上版本
- 完整中文注释与文档字符串，配套单元测试与 GitHub Actions CI

## 目录结构

```text
embodied-utils/
├── .github/workflows/ci.yml   # 持续集成流水线
├── embodied_utils/            # 核心源码
│   ├── __init__.py
│   ├── geometry.py
│   ├── safety.py
│   └── trajectory.py
├── tests/                     # 单元测试
│   ├── test_geometry.py
│   ├── test_safety.py
│   └── test_trajectory.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## 快速开始

```bash
git clone https://github.com/ZhongguancunSmartCity/test.git
cd test
python -m unittest discover -v
```

调用示例：

```python
from embodied_utils import path_length, resample_by_step

trajectory = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
print(path_length(trajectory))            # 2.0
print(resample_by_step(trajectory, 0.5))  # 按 0.5 的步长重采样
```

碰撞检测示例：

```python
from embodied_utils import first_collision_index

trajectory = [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
obstacles = [(5.0, 0.0, 0.5)]  # (x, y, radius)

index = first_collision_index(trajectory, obstacles, robot_radius=0.3)
print(index)  # 1，第 1 个航点与障碍物发生碰撞
```

## 协作流程验证

本仓库用于验证 GitHub 的分支保护与合并策略，可按以下步骤操作：

> 完整的单账号手动测试步骤（含预期输出、验收清单与常见问题）见
> [GitHub 分支保护与 PR 合并流程 —— 手动测试手册](docs/github-workflow-test-guide.md)。

1. 为 `main` 分支开启保护规则（要求 Pull Request 审核通过、并要求状态检查通过）
2. 直接向 `main` 推送应被拒绝，提示 `protected branch` 相关错误
3. 从 `main` 切出特性分支提交改动，推送后发起 Pull Request
4. 通过审核与状态检查后合并 PR，确认 `main` 上出现对应提交

## License

MIT
