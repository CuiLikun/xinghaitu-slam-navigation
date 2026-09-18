# 从旧工作空间迁移

[返回首页](../README.md)

## 目录对应

| 旧目录 | 新目录 |
| --- | --- |
| `src/FAST_LIO` | `packages/localization/fast_lio` |
| `src/terrain_analysis`、`far_planner`、`local_planner`、`boundary_handler`、`visibility_graph_msg` | `packages/navigation/` 下同名目录 |
| `src/graph_decoder`、`goalpoint_rviz_plugin`、`teleop_rviz_plugin` | `packages/visualization/` 下同名目录 |
| `src/smartcar_control`、`smartcar_description` | `packages/robot/` 下同名目录 |
| `src/livox_ros_driver` | `third_party/livox_ros_driver` |
| `src/serui` | `third_party/serui` |
| `src/CMakeLists.txt` | 移除；由外部工作空间的 catkin 创建 |
| 包内 Python 可执行节点的 `src/*.py` | 各包 `scripts/*.py` |

ROS 包名与节点可执行文件名保留。现有 `$(find fast_lio)` 等引用仍可用；手写仓库相对路径需要更新。

## 推荐迁移方式

保留旧目录作为备份，在新工作空间中重新克隆并编译，按[安装指南](installation.md)操作。将旧版经过标定的 YAML 复制到单独的机器人配置目录，通过新入口的 `config_file` / `planner_config` 参数加载。不要复制旧 `build/`、`devel/`、`install/`。

## 行为变化

- 本仓库改为可嵌入已有工作空间的多包源码仓库，不再在仓库根目录直接执行 `catkin_make`。
- 局部规划与跟踪使用 `/local_path`，FAST-LIO 的 `/path` 保留为历史轨迹；自定义 RViz 和下游订阅要区分两者。
- 新统一导航入口默认不启动速度转换器，示例速度为 `0.2 m/s`；旧独立局部 launch 保持其原有默认值。
- FAST-LIO 输出从源码内目录改为可配置的运行目录；旧独立入口默认使用节点工作目录，统一入口默认 `~/.ros/xinghaitu`。
- `smartcar_gazebo.launch` 默认加载空世界，通过 `world_name` 传入外部场景。
- 底盘几何与加速度参数优先读取 launch 中的私有参数，兼容原全局参数作为后备；`~dist_wheels` 对应轮距。
- `serui` 不再置于源码包目录；按[串口库说明](../third_party/serui/README.md)显式安装或配置 Python 路径。
- Livox 恢复构建入口；未安装 SDK 时使用 `-DLIVOX_BUILD_DRIVER=OFF` 构建消息与其他模块。
