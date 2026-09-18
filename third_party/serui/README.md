# serui 厂商串口依赖

本目录保留历史底盘依赖：Python 接口、Cython 源码、生成的 C++ 和 `impl3.so`。它不是 ROS 包，`CATKIN_IGNORE` 明确排除 catkin 自动发现；不会由本仓库自动安装原生二进制。

`impl3.so` 与编译时 CPU 架构、Python ABI 和系统库绑定。目录中的 Cython 引用厂商头文件/库，现有仓库不提供完整的跨平台构建工具链；请从硬件供应方取得与目标机匹配的安装包或 SDK。

仅在可信目标机上确认兼容性后，可以临时测试随附版本：

```bash
# 修改为你的仓库绝对路径。该层目录内包含 serui/。
export PYTHONPATH="$HOME/catkin_ws/src/xinghaitu-slam-navigation/third_party${PYTHONPATH:+:$PYTHONPATH}"
python3 -c "from serui import SerUiCl; print('serui import OK')"
```

该路径配置不验证 ABI 或运动控制正确性。正式部署优先按厂商方式安装到目标 Python 环境，再运行 `smartcar_control`。仿真脚本不导入 `serui`。
