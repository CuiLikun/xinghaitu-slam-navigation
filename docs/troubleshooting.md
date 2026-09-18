# 排障与验证

[返回首页](../README.md) · [安装指南](installation.md)

## 常见问题

| 现象 | 检查方向 |
| --- | --- |
| `catkin_make` 找不到源码 | 在 `~/catkin_ws` 执行；本仓库放在 `~/catkin_ws/src/` 下 |
| `rospack` 找不到包 | 当前终端 source `devel/setup.bash` 或 `install/setup.bash` |
| 出现同名包错误 | 工作空间或 overlay 中只保留每个 ROS 包的一份源码 |
| 找不到 Livox SDK | bag / 外部驱动使用 `LIVOX_BUILD_DRIVER=OFF`；硬件节点按 SDK 文档安装依赖 |
| `Cannot read input files` | 检查 `path_folder` 内三份 PLY 和 `correspondences.txt` 是否成套 |
| `ImportError: serui` | 见厂商库说明，核查 Python 搜索路径和原生 ABI |
| 无点云 / 无里程计 | `rosbag info`、`rostopic hz`，检查传感器字段、时间戳和 YAML |
| TF 跳变或多父节点 | 排查重复 TF 发布者，确认外参与机体系约定 |
| 地形或避障范围不合理 | 核对高度、车体尺寸、世界系点云和参考路径碰撞半径 |
| 默认启动后底盘不动 | 统一入口默认关闭 Twist 转换器，且不启动底盘；先独立验证控制链路 |
| 安装后找不到 launch / YAML | 重新执行 `catkin_make install`，source 对应安装空间 |

## 可重复检查

不依赖 ROS 的仓库检查：

```bash
python3 tools/check_repository.py
```

检查 13 个 ROS 包入口、XML、launch 参数契约、Python 语法、底盘私有参数与旧全局参数的兼容性、三份参考路径的哈希与行数、碰撞表索引、局部路径隔离和文档链接。

完成 ROS 构建后，在未启动其他导航实例的独立测试环境中运行：

```bash
source ~/catkin_ws/devel/setup.bash
python3 tools/smoke_ros.py
```

脚本临时启动无硬件导航，检查节点存活、重映射、默认无 `/cmd_vel` 输出及资源查找，再验证 FAST-LIO 在外部目录创建运行输出，最后结束自己启动的进程。请勿在正在控制机器人的 ROS master 上运行。

GitHub Actions 在 Noetic/Focal 容器中构建所有 ROS 包（Livox 仅消息模式），执行 `catkin_make install`，分别验证 devel 与 install 空间。以 [Actions 实际运行结果](https://github.com/CuiLikun/xinghaitu-slam-navigation/actions/workflows/ros1.yml) 为准。

## 尚未覆盖

CI 无真实传感器数据，不评价建图精度、规划成功率或停车距离，也不测试厂商 `serui` 原生扩展、完整 Livox SDK 硬件驱动、Mid-360 消息适配和 Gazebo 动态仿真。这些仍需设备与数据支持。
