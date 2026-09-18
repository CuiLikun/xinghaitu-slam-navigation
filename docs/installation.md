# 安装与运行

[返回首页](../README.md) · [机器人接入](integration.md) · [排障](troubleshooting.md)

## 工作空间边界

本仓库是一组 ROS1 包，放在 **catkin 工作空间的 `src/` 内**。不要在仓库根目录执行 `catkin_make`。已有工作空间可直接复用，先确认没有另一份 `fast_lio`、`local_planner` 或 `livox_ros_driver` 等同名包。

目标组合为 Ubuntu 20.04、ROS Noetic、Python 3.8。ROS Noetic 已于 2025-05-31 结束官方维护（[ROS 官方公告](https://www.ros.org/blog/noetic-eol/)）；其他 ROS1 发行版不在当前验证范围内。

## 依赖与编译

先按 ROS 官方方式安装 Noetic，并确保 `rosdep` 可用。以下步骤不会安装厂商底盘二进制库：

```bash
source /opt/ros/noetic/setup.bash
sudo apt update
sudo apt install build-essential cmake git python3-rosdep python3-dev
# 仅在 /etc/ros/rosdep/sources.list.d 尚未初始化时执行：
sudo rosdep init
rosdep update --include-eol-distros
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/CuiLikun/xinghaitu-slam-navigation.git
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src --rosdistro noetic -y
catkin_make -j2 -DLIVOX_BUILD_DRIVER=OFF -DPYTHON_EXECUTABLE=/usr/bin/python3
source devel/setup.bash
```

低内存机器可改为 `-j1 -l1`。`rosdep` 必须成功后再编译；不要跳过未解决的依赖继续构建。

## 安装空间

包内节点、Python 脚本、launch、配置、模型和参考路径带有安装规则：

```bash
cd ~/catkin_ws
catkin_make install -j2
source install/setup.bash
rospack find xinghaitu_bringup
roslaunch xinghaitu_bringup navigation.launch rviz:=false
```

安装空间包含随附 ROS 包资源，但不包含 `third_party/serui` 的自动安装。FAST-LIO 运行输出默认位于 ROS 运行目录，统一启动入口指定为 `~/.ros/xinghaitu`，不要求源码目录可写。

## 建图与回放

从 `packages/localization/fast_lio/config/` 复制适合传感器的 YAML 到你自己的配置目录，修改点云和 IMU 话题、点类型、每点时间字段单位和外参。示例 `velodyne.yaml` 中的外参不代表你的设备标定。

三个终端均先 `source ~/catkin_ws/devel/setup.bash`：

```bash
# 终端 1：先设置模拟时间，再等待 bag 的 /clock。
roslaunch xinghaitu_bringup mapping.launch \
  config_file:=$HOME/robot_config/lidar.yaml use_sim_time:=true rviz:=false
```

```bash
# 终端 2：统一启动导航；不会连接底盘。
roslaunch xinghaitu_bringup navigation.launch use_sim_time:=true
```

```bash
# 终端 3：bag 应含原始传感器数据；避免重放旧的 TF、/Odometry 或控制话题。
rosbag play your_recording.bag --clock --pause
# 节点准备好后按空格开始。
```

若 bag 包含多种输出，用 `rosbag info` 查明实际话题，再通过 `--topics` 只选择需要的点云和 IMU。两个入口的 `use_sim_time` 必须一致。实机实时传感器用 `false`，且需单独启动驱动。

统一建图入口默认关闭 PCD 保存。需要导出时设置：

```bash
roslaunch xinghaitu_bringup mapping.launch \
  config_file:=$HOME/robot_config/lidar.yaml \
  pcd_save:=true output_directory:=$HOME/maps/session_01
```

PCD 写入该目录的 `PCD/`；累计策略由 YAML 中 `pcd_save/interval` 控制。原有 `fast_lio mapping_*.launch` 仍可用，保留各自传感器的预处理参数。

## Livox 驱动

FAST-LIO 编译时依赖 `livox_ros_driver/CustomMsg`，即使输入是 Velodyne PointCloud2，也需要生成这个消息包。

| 构建选项 | 产物 | 适合场景 |
| --- | --- | --- |
| `-DLIVOX_BUILD_DRIVER=OFF` | Livox 消息及其他 ROS 包 | rosbag、外部驱动、非 Livox 雷达 |
| `-DLIVOX_BUILD_DRIVER=ON`（CMake 默认） | 额外构建 `livox_ros_driver_node` | 使用随附 Livox v1 驱动，需要 SDK |

完整驱动需事先安装 [Livox-SDK v1](https://github.com/Livox-SDK/Livox-SDK)，再构建本仓库；CMake 不自动下载 SDK 或修改系统。遵循 SDK 仓库说明安装到标准前缀，或传入 `LIVOX_SDK_INCLUDE_DIR` 与 `LIVOX_SDK_LIBRARY`，然后：

```bash
cd ~/catkin_ws
catkin_make -j2 -DLIVOX_BUILD_DRIVER=ON
source devel/setup.bash
roslaunch livox_ros_driver livox_lidar_msg.launch
```

**Mid-360 / HAP** 使用 [livox_ros_driver2](https://github.com/Livox-SDK/livox_ros_driver2)，不由本仓库 v1 驱动直接支持。当前 FAST-LIO 自定义消息订阅类型仍为 `livox_ros_driver/CustomMsg`，不能仅把 driver2 的 CustomMsg 话题改名就当成兼容。需选择与预处理字段匹配的 PointCloud2 输入，或另行实现并验证消息适配；`mid360.yaml` 的存在不代表这条链路已经验证。
