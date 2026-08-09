# 星海图机器人无先验地图自主建图与导航

`xinghaitu-slam-navigation` 是面向星海图四轮移动机器人的 ROS1/catkin 工作空间。系统在未知环境中使用激光雷达和 IMU 进行 FAST-LIO 状态估计与建图，再将里程计和配准点云交给 FAR Planner 完成地形分析、路径规划与局部避障，最后由底盘控制节点执行速度指令。

> **项目状态：尚未在实机运行或完成端到端验证。** 本仓库含有实机与 Gazebo 相关代码，但下文的实机启动命令仅是基于源码接口整理的部署建议，不代表已经在星海图机器人上验证可用。首次实机测试前，必须完成雷达—IMU 外参、TF 树、话题映射、车体尺寸和速度上限的校准；不要直接使用示例参数。

## 系统组成

```text
LiDAR + IMU
    │
    ▼
FAST-LIO ──► /Odometry、/cloud_registered
    │                         │
    └─────────────► terrain_analysis ──► /terrain_map
                                      │
                                      ▼
                              FAR Planner + local planner
                                      │
                                      ▼
                               /cmd_vel_stamped
                                      │
                                      ▼
                               星海图四轮底盘
```

主要软件包如下：

| 模块 | ROS 包 | 作用 |
| --- | --- | --- |
| 定位与建图 | `fast_lio` | FAST-LIO 激光惯性里程计与点云建图 |
| 雷达驱动 | `livox_ros_driver` | Livox 雷达 ROS 驱动与录包工具 |
| 地形感知 | `terrain_analysis` | 由配准点云生成可通行地形信息 |
| 导航规划 | `far_planner`、`local_planner` | 全局可见图规划、局部路径跟踪与避障 |
| 交互可视化 | `goalpoint_rviz_plugin`、`teleop_rviz_plugin`、`graph_decoder` | RViz 目标点、手动接管与图保存/读取 |
| 底盘与仿真 | `smartcar_control`、`smartcar_description`、`serui` | 四轮底盘控制、URDF/Xacro、Gazebo 仿真和串口/界面相关功能 |

## 目录结构

```text
.
├── src/
│   ├── FAST_LIO/                 # FAST-LIO
│   ├── livox_ros_driver/         # Livox 驱动
│   ├── terrain_analysis/         # 地形分析
│   ├── far_planner/              # FAR 全局规划
│   ├── local_planner/            # 局部规划与路径跟踪
│   ├── smartcar_control/         # 四轮底盘控制
│   ├── smartcar_description/     # 机器人模型与仿真
│   └── ...
└── README.md
```

## 环境要求

- Ubuntu 20.04 + ROS Noetic 为推荐组合；部分代码也适用于 Ubuntu 18.04 + ROS Melodic。
- 已安装 ROS 桌面版、`catkin`、PCL、Eigen、Boost、`tf`、RViz 与 Gazebo（如使用仿真）。
- 实机需接入与 `FAST_LIO/config/` 中配置相符的激光雷达和 IMU；Livox 雷达还需正确连接 `livox_ros_driver`。

安装常用系统依赖：

```bash
sudo apt update
sudo apt install build-essential cmake git libpcl-dev libeigen3-dev
```

其余 ROS 依赖由 `rosdep` 解析：

```bash
sudo rosdep init              # 仅首次需要
rosdep update
cd ~/xinghaitu-slam-navigation
rosdep install --from-paths src --ignore-src -r -y
```

## 编译

```bash
git clone https://github.com/CuiLikun/xinghaitu-slam-navigation.git
cd xinghaitu-slam-navigation
catkin_make
source devel/setup.bash
```

建议把最后一行加入 `~/.bashrc`，或在每个新终端启动系统前手动执行。若编译失败，先确认 ROS 发行版与 Ubuntu 版本匹配，并重新运行 `rosdep install`。

## 实机集成与验证建议（尚未验证）

建议先用传感器 rosbag 完成离线验证，再在空旷场地以低速、有人可立即急停的方式分阶段测试。不要在首次上电时同时启用自主规划和底盘驱动。

### 1. 先验证传感器与 FAST-LIO

在 `src/FAST_LIO/config/` 中选择与传感器相符的配置，并校准以下项目：

- `common.lid_topic` 和 `common.imu_topic` 必须分别匹配真实点云与 IMU 话题。仓库的 Velodyne 示例使用 `/velodyne_points` 与 `/imu_data`；Livox 配置通常使用 `/livox/imu`，实际名称应以 `rostopic list` 为准。
- `mapping.extrinsic_T` 与 `mapping.extrinsic_R` 是雷达相对 IMU 的外参。它们必须来自可靠标定；若未知，请保持保守、先完成标定，不能把示例的 `[0, 0, 0.28]` 当作实机值。
- 核查 LiDAR 和 IMU 的时间戳单调且同步。`time_sync_en` 只应在无法使用外部时间同步时启用；不确定时间偏移时保持 `time_offset_lidar_to_imu: 0.0`。
- 首次运行时建议将 `pcd_save.pcd_save_en` 设为 `false`，避免长时间运行因持续保存点云占满磁盘或内存。

FAST-LIO 运行后，先只检查下表接口与 RViz 中的轨迹/点云质量，确认无跳变再接入规划器：

| 接口 | 类型/坐标系 | 用途 |
| --- | --- | --- |
| `/Odometry` | `nav_msgs/Odometry`，`map → body` | FAST-LIO 位姿估计 |
| `/cloud_registered` | `sensor_msgs/PointCloud2`，`map` | 配准后的世界系点云 |
| `/cloud_registered_body` | `sensor_msgs/PointCloud2`，`body` | 车体系点云，用于诊断 |
| `/path` | `nav_msgs/Path`，`map` | FAST-LIO 轨迹 |

### 2. 对齐 TF 树

本项目中 FAST-LIO 会发布 `map → body`。底盘包的示例使用 `base_footprint`、`imu_link` 和 `laser_front_link` 等坐标系；局部规划器又默认使用 `body` 与 `vehicle`。实机上应先确定一套唯一的坐标系命名和父子关系，再通过静态变换适配各包，推荐目标结构如下：

```text
map ──(FAST-LIO)──► body（IMU/状态估计机体系）
                         └──► base_footprint（机器人底盘中心）
                               ├──► laser_link
                               └──► imu_link（如与 body 不同）
```

- 采用 ROS 标准方向：`x` 前、`y` 左、`z` 上；`base_footprint` 位于地面投影的底盘中心。
- 每条 TF 边只能有一个发布者。特别是 `smartcar_control/launch/base.launch` 的 `publish_odom_transform` 和 FAST-LIO 的 `map → body` 不应与其他节点发布同一条或相互矛盾的边。
- 若 `body` 就是 IMU 机体系，应发布经外参校验的 `body → base_footprint` 静态变换；若使用不同名称，应在 launch 中统一重命名或增加明确的静态转换，不能让一个子坐标系同时拥有两个父坐标系。
- 使用以下命令检查树中没有断链、循环或重复发布，并确认 RViz 的 Fixed Frame 为 `map`：

```bash
rosrun tf view_frames
rosrun tf tf_echo map body
rosrun rqt_tf_tree rqt_tf_tree
```

### 3. 显式核对话题映射

现有 launch 文件已经包含部分重映射，实机接入前应逐项核对，而不是依赖默认名字：

| 数据流 | 当前源码约定 | 实机接入动作 |
| --- | --- | --- |
| 传感器 → FAST-LIO | `lid_topic`、`imu_topic` 由 FAST-LIO YAML 指定 | 在对应 YAML 中改为真实传感器话题，或在启动时 remap |
| FAST-LIO → 地形/局部规划 | `/Odometry`、`/cloud_registered` | `terrain_analysis` 与 `local_planner` 已重映射到这两个话题；确认消息持续发布且时间戳正常 |
| FAST-LIO → FAR Planner | `/Odometry`、`/cloud_registered`，地形图为 `/terrain_map` | 通过 `far_planner.launch` 的 `odom_topic`、`scan_cloud_topic`、`terrain_cloud_topic`、`terrain_local_topic` 参数显式指定 |
| 局部规划 → 底盘 | `/cmd_vel_stamped` → `cmd_vel_converter.py` → `/cmd_vel` | 底盘驱动 `4_drive_control.py` 订阅 `/cmd_vel`（`geometry_msgs/Twist`）；先用低速手动消息确认正负方向、限幅和超时急停 |

例如，若保持当前默认接口，可用下面的方式显式启动 FAR Planner：

```bash
roslaunch far_planner far_planner.launch \
  odom_topic:=/Odometry \
  scan_cloud_topic:=/cloud_registered \
  terrain_cloud_topic:=/terrain_map \
  terrain_local_topic:=/terrain_map
```

### 4. 底盘与安全联调顺序

1. 让底盘离地或预留充足安全距离，只启动底盘驱动；核对串口设备、波特率、轮径、轴距、轮距和转向方向。
2. 使用低频、零附近的 `/cmd_vel` 手动测试前进、后退、左右转和超时停车，确认 `/enable_cmd_vel` 与急停有效。
3. 启动 FAST-LIO，静止初始化后缓慢手推或遥控机器人，检查 `map → body` 位姿方向与真实运动一致。
4. 只启动 `terrain_analysis`，确认 `/terrain_map` 合理反映地面和障碍物。
5. 启动 FAR Planner 与 local planner，但先保持自主速度很低；验证设定目标、停止、手动接管和恢复导航。
6. 完成多次可重复测试后，再逐步提高 `maxSpeed`、`autonomySpeed` 和加速度限制。

## 参考启动顺序：实机建图与导航

以下命令是待上述验证完成后的参考顺序（均假设已 `source devel/setup.bash`）：

```bash
# 终端 1：启动传感器驱动与 FAST-LIO。
# Velodyne 示例；Livox/Mid-360 等请改用对应 launch 与配置。
roslaunch fast_lio mapping_velodyne.launch
```

```bash
# 终端 2：从 /Odometry 和 /cloud_registered 生成地形图
roslaunch terrain_analysis terrain_analysis.launch
```

```bash
# 终端 3：启动全局规划、局部规划和 RViz
roslaunch far_planner far_planner.launch
roslaunch local_planner local_planner.launch
```

在 RViz 中使用 `Goalpoint` 工具设置目标点。FAR Planner 将优先在已知自由空间中规划；必要时会扩展到未知区域。运行中可通过 `Smart Joystick` 接管，或使用 `Resume Navigation to Goal` 恢复目标导航。

## 使用 rosbag 回放

先启动 FAST-LIO 和导航模块，再在另一个终端回放数据：

```bash
rosbag play your_recording.bag --clock
```

如使用仿真时间，请确保 launch 或参数服务器启用 `use_sim_time`。回放前也应核对 bag 中的点云/IMU 话题是否与 FAST-LIO 配置一致。

## Gazebo 仿真

```bash
roslaunch smartcar_description smartcar_gazebo.launch
```

该 launch 文件目前含有 AWS RoboMaker Small House world 的本地绝对路径。使用前请把 `smartcar_gazebo.launch` 中的 `world_name` 改为本机 world 文件路径；如需该环境，请单独获取 `aws-robomaker-small-house-world` 的 ROS1 分支，并设置：

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/xinghaitu-slam-navigation/src/aws-robomaker-small-house-world/models
```

仿真中启动导航前，同样需要确保仿真发布的里程计、点云与上述 `/Odometry`、`/cloud_registered` 接口一致。

## 常见排查

- **找不到 ROS 包**：确认在工作空间根目录执行了 `catkin_make`，并在当前终端执行 `source devel/setup.bash`。
- **没有点云或 IMU 数据**：用 `rostopic list`、`rostopic echo` 检查实际话题，并与 FAST-LIO 配置对照。
- **TF 报错或轨迹跳变**：用 `rosrun tf tf_monitor` 或 `rqt_tf_tree` 检查坐标树，随后复核外参和时间同步。
- **规划器不出路径或误判障碍**：检查 `/terrain_map`、`/cloud_registered` 与 `/Odometry` 是否持续发布；再根据环境调节地形分析和局部规划参数。
- **机器人运动方向或速度异常**：立即切换手动/急停，检查 `cmd_vel_stamped` 到底盘驱动的转换、轮距/尺寸和最大速度设置。

## 许可证与致谢

本仓库是面向星海图机器人的 ROS1 自主建图与导航工作空间。第三方依赖及各 ROS 包的许可、署名和使用条件仍以其随附源码为准。
