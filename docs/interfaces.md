# 接口与包清单

[返回首页](../README.md) · [机器人接入](integration.md)

## 包的职责

| 分组 | ROS 包 | 职责 |
| --- | --- | --- |
| bringup | `xinghaitu_bringup` | 建图、导航组合入口 |
| localization | `fast_lio` | 激光惯性里程计、点云配准 |
| navigation | `terrain_analysis` | 地形分析 |
| navigation | `far_planner` | 可见图全局规划 |
| navigation | `local_planner` | 路径选择、跟踪及可选速度转换 |
| navigation | `boundary_handler` | 边界图处理 |
| navigation | `visibility_graph_msg` | 导航图消息 |
| visualization | `graph_decoder` | 图保存、读取与解码 |
| visualization | `goalpoint_rviz_plugin` | RViz 目标点交互 |
| visualization | `teleop_rviz_plugin` | RViz 手动控制 |
| robot | `smartcar_control` | 四轮底盘及仿真控制 |
| robot | `smartcar_description` | URDF/Xacro、模型和控制器配置 |
| third_party | `livox_ros_driver` | Livox v1 消息与可选驱动节点 |

`serui` 是厂商 Python/原生库，不是 ROS 包。

## 默认数据流

| 话题 | 消息 | 发布者 → 消费者 | 坐标语义 |
| --- | --- | --- | --- |
| YAML 指定的点云与 IMU | 传感器类型对应消息 | 外部驱动 → FAST-LIO | 原始传感器坐标 |
| `/Odometry` | `nav_msgs/Odometry` | FAST-LIO → 地形与规划 | `map` 中的 `body` 位姿 |
| `/cloud_registered` | `sensor_msgs/PointCloud2` | FAST-LIO → 地形与规划 | `map`，已配准 |
| `/terrain_map` | `sensor_msgs/PointCloud2` | terrain_analysis → FAR / local | 世界系地形 |
| `/way_point` | `geometry_msgs/PointStamped` | FAR → local | 世界系局部目标 |
| `/path` | `nav_msgs/Path` | FAST-LIO → 可视化 | `map` 中历史轨迹 |
| `/local_path` | `nav_msgs/Path` | localPlanner → pathFollower | `vehicle` 中的控制路径 |
| `/cmd_vel_stamped` | `geometry_msgs/TwistStamped` | pathFollower → 控制适配 | `vehicle` |
| `/cmd_vel` | `geometry_msgs/Twist` | 可选转换器 → 底盘 | 无 header，接入者负责约定 |

`/path` 和 `/local_path` 必须分开。路径跟踪器不应该消费 FAST-LIO 的历史轨迹。

## navigation.launch 参数

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `odom_topic` | `/Odometry` | 定位输入，透传到所有规划模块 |
| `cloud_topic` | `/cloud_registered` | 世界系点云输入 |
| `terrain_topic` | `/terrain_map` | 地形模块输出及规划模块输入 |
| `planner_config` | FAR `config/default.yaml` | 完整 FAR 配置文件路径 |
| `path_folder` | local_planner `paths/` | 四份匹配的局部路径数据 |
| `max_speed` / `autonomy_speed` | `0.2` / `0.2` | 局部速度示例上限 / 自主速度，m/s |
| `vehicle_length/width/height` | `0.85 / 0.6 / 0.75` | 局部规划长宽、地形分析高度，m |
| `sensor_offset_x/y` | `0.0 / 0.0` | 局部规划传感器偏移，m |
| `enable_cmd_vel_converter` | `false` | 是否把带时间戳速度转换成 Twist |
| `cmd_vel_topic` | `/cmd_vel` | 转换器输出 |
| `cmd_vel_stamped_topic` | `/cmd_vel_stamped` | 局部控制输出 |
| `publish_body_to_vehicle_tf` | `true` | 发布默认零静态变换 |
| `rviz` / `use_sim_time` | `true / false` | 可视化 / ROS 时钟来源 |

## mapping.launch 参数

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `config_file` | FAST-LIO `config/velodyne.yaml` | 传感器、外参和建图配置 |
| `rviz` | `true` | 显示 FAST-LIO 可视化 |
| `use_sim_time` | `false` | rosbag 回放时设置 `true` |
| `pcd_save` | `false` | 覆盖 YAML 中保存开关 |
| `output_directory` | `~/.ros/xinghaitu` | `Log/` 与 `PCD/` 输出位置 |

底层包的原 launch 仍可独立使用。旧 `local_planner.launch` 保留速度转换器默认开启与 `2.0 m/s` 速度参数；建议新用户从统一入口开始，避免误用旧默认值。
