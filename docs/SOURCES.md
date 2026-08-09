# 源码来源与合并记录

本仓库将原先独立维护的三个 ROS/catkin 工作空间合并为同一工作空间；各软件包保持原目录名和源码内容，以减少合并对运行行为的影响。

| 原仓库 | 纳入内容 | 固定提交 |
| --- | --- | --- |
| [base_4drive](https://github.com/CuiLikun/base_4drive) | 星海图四轮底盘的模型、控制与仿真相关包 | `fcc3ecdcb82a796bb2c5f96a2371041b29daf5ef` |
| [far_planner](https://github.com/CuiLikun/far_planner) | 地形分析、全局/局部规划、可视化与消息包 | `a74e26c6487d858b5772a319fbff7c85f5aeef34` |
| [fastlio_ws](https://github.com/CuiLikun/fastlio_ws) | FAST-LIO 与 Livox ROS 驱动 | `d312497e15c0ab80ce0cae457ba7be686870d6fc` |

三者原有的 `src/CMakeLists.txt` 内容相同，合并工作空间保留一份该文件。此文档用于保留来源与版本追溯；后续更新上游时，请同时更新本表和相应变更说明。
