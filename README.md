# 星海图机器人无先验地图自主建图与导航

`xinghaitu-slam-navigation` 是面向星海图四轮移动机器人的 ROS1/catkin 工作空间。系统在未知环境中使用激光雷达和 IMU 进行 FAST-LIO 状态估计与建图，再将里程计和配准点云交给 FAR Planner 完成地形分析、路径规划与局部避障，最后由底盘控制节点执行速度指令。

> 本仓库同时含有实机与 Gazebo 仿真相关代码。初次在实机运行前，必须完成雷达—IMU 外参、坐标系、话题名、车体尺寸和速度上限的校准；不要直接使用示例参数。

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

## 实机部署前配置

1. 在 `src/FAST_LIO/config/` 中选择并校准传感器配置（例如 `velodyne.yaml`），确认点云和 IMU 话题、外参与时间同步。
2. 确认 FAST-LIO 输出与导航模块的约定一致：`/Odometry` 为状态估计，`/cloud_registered` 为配准点云。`terrain_analysis` 和 `local_planner` 已将内部输入重映射至这两个话题。
3. 根据星海图机器人实际尺寸、传感器安装位置和安全速度，调整 `local_planner/launch/local_planner.launch` 内的车长、车宽、传感器偏移、速度和加速度参数。
4. 确认底盘控制接口接收的速度话题。局部规划器输出经 `cmd_vel_converter.py` 转为 `/cmd_vel_stamped`；如实机驱动使用不同消息类型或话题，请在接入前完成桥接和低速测试。
5. 在空旷、安全区域验证 TF 树、急停、遥控接管与速度方向，再开始自主模式。

## 快速启动：实机建图与导航

在三个终端分别执行下列命令（均假设已 `source devel/setup.bash`）：

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
