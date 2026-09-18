# 贡献指南

保持 ROS 包名和对外接口稳定，把机器人特有配置放在启动组合或自己的配置包中。改动话题、坐标系、路径数据或默认控制行为时，同步更新 [接口文档](docs/interfaces.md) 与 [迁移说明](docs/migration.md)。

提交前运行 `python3 tools/check_repository.py`。涉及构建、安装或 launch 的变更还需通过 Noetic 工作流；涉及导航行为的变更应提供可重复的 rosbag 条件及结果，不能仅以“编译通过”作为算法验证。

新 Python 节点放在 `scripts/`，使用 `catkin_install_python`；新的运行资源补充 CMake 安装规则。不要提交 `build/`、`devel/`、Python 缓存、录包或实测地图；局部规划器的参考路径数据属于必需运行资源，允许入库。

保留第三方许可证和署名。仓库没有统一许可证，不要用新许可证覆盖已有第三方代码。
