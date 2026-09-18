#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, TwistStamped

def callback(msg):
    pub.publish(msg.twist)

if __name__ == '__main__':
    rospy.init_node('cmd_vel_converter')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    rospy.Subscriber('/cmd_vel_stamped', TwistStamped, callback)
    rospy.spin()
