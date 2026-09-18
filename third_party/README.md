# 第三方组件

| 目录 | 内容 | 集成方式 |
| --- | --- | --- |
| [livox_ros_driver](livox_ros_driver/README.md) | Livox v1 驱动源码与消息 | catkin 递归发现内部包；SDK 另行安装 |
| [serui](serui/README.md) | 厂商串口 Python/Cython 与原生库 | 非 catkin 包，目标机验证后手动使用 |

保留随附源码结构与许可。Livox 缺失的 CMake 入口在本次整理中重建，参考其上游构建关系，并增加显式 SDK 查找及消息单独构建选项；不再由构建过程自动下载或安装 SDK。

局部规划缺失的参考路径恢复自固定版本 `7ae94b72206430a399ae012f49715cf51fadb0e0`，来源记录在 [assets.json](../packages/navigation/local_planner/paths/assets.json)。恢复前逐字比较了现有生成器与碰撞表，三份 PLY 的 SHA256 由离线检查脚本验证。

许可范围以具体随附文件为准：[Livox MIT](livox_ros_driver/LICENSE.txt)、[FAST-LIO LICENSE](../packages/localization/fast_lio/LICENSE)。部分现有包的声明与随附许可不一致，底盘组件许可尚不明确；没有为它们补造授权。
