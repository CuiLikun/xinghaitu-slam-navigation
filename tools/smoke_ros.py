#!/usr/bin/env python3
"""Launch navigation without hardware; check live nodes, remaps and install resources."""
import os
from pathlib import Path
import signal
import subprocess
import time
import rosgraph
import rosnode
import rospy
import rospkg

process = subprocess.Popen(['roslaunch', 'xinghaitu_bringup', 'navigation.launch', 'rviz:=false',
                            'odom_topic:=/test/odom', 'cloud_topic:=/test/cloud',
                            'terrain_topic:=/test/terrain'], start_new_session=True)
try:
    expected = {'/terrainAnalysis', '/far_planner', '/graph_decoder', '/localPlanner', '/pathFollower'}
    deadline = time.monotonic() + 45
    master = rosgraph.Master('/ci_check')
    while time.monotonic() < deadline:
        assert process.poll() is None, 'roslaunch exited early'
        try:
            if expected <= set(rosnode.get_node_names()):
                break
        except (OSError, rosgraph.MasterError):
            pass
        time.sleep(1)
    else:
        raise AssertionError('Navigation nodes did not start')
    time.sleep(4)
    assert all(rosnode.rosnode_ping(n, max_count=1) for n in expected)
    publishers, subscribers, _ = master.getSystemState()
    pub, sub = dict(publishers), dict(subscribers)
    assert '/cmd_vel' not in pub, 'Default bringup must not publish unstamped hardware commands'
    assert '/pathFollower' in sub.get('/local_path', [])
    assert '/localPlanner' in pub.get('/local_path', [])
    assert '/pathFollower' not in sub.get('/path', [])
    assert {'/terrainAnalysis', '/far_planner', '/localPlanner', '/pathFollower'} <= set(sub['/test/odom'])
    assert {'/far_planner', '/localPlanner'} <= set(sub['/test/terrain'])
    assert abs(rospy.get_param('/pathFollower/maxSpeed') - 0.2) < 1e-9
    assert abs(rospy.get_param('/localPlanner/autonomySpeed') - 0.2) < 1e-9
    for pkg, rel in [('far_planner', 'config/default.yaml'), ('far_planner', 'rviz/default.rviz'),
                     ('graph_decoder', 'config/default.yaml'), ('local_planner', 'paths/paths.ply'),
                     ('fast_lio', 'config/velodyne.yaml'), ('smartcar_description', 'urdf/xacro/smartcar.xacro')]:
        assert (Path(rospkg.RosPack().get_path(pkg)) / rel).is_file()
    print('PASS: live navigation nodes, remapped topics, separated paths, default command isolation and resources')
finally:
    os.killpg(process.pid, signal.SIGINT)
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
