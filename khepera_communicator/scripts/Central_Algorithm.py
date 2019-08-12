#!/usr/bin/env python

#!/usr/bin/env python
# license removed for brevity
import rospy
import math
import time
import rosnode
# Import message file
from std_msgs.msg import String
from khepera_communicator.msg import K4_controls, SensorReadings
from geometry_msgs.msg import TransformStamped

start = time.time()

rospy.init_node('Central_Algorithm', anonymous=True)

# Get all the node names for all the currently running K4_Send_Cmd nodes (all running Kheperas)
# Get the node names of all the current running nodes
node_list = rosnode.get_node_names()

# Find the nodes that contains the "K4_Send_Cmd_" title
khep_node_list = [s for s in node_list if "K4_Send_Cmd_" in s]
ip_num_list = [x[13:16] for x in khep_node_list]
khep_node_cnt = len(khep_node_list)

# Establish all the publishers to each "K4_controls_" topic, corresponding to each K4_Send_Cmd node, which corresponds to each Khepera robot
pub = []
for i in range(khep_node_cnt):
	pub.append(rospy.Publisher('K4_controls_' + str(ip_num_list[i]), K4_controls, queue_size = 10))

# This callback function is where the centralized swarm algorithm, or any algorithm should be
# data is the info subscribed from the vicon node, contains the global position, velocity, etc
# the algorithm placed inside this callback should be published to the K4_controls topics
# which should have the K4_controls message type:
# Angular velocity: ctrl_W
# Linear velocity: ctrl_V
def callback(data, args):
	# i indicates which subsciber this callback function belongs to,
	# thus it knows which publisher/topic to publish to
	i = args


	# The message to be published
	control_msgs = K4_controls()
	
	# Algorithms go here
	"""
	end = time.time()
	t = end - start
	control_msgs.ctrl_W = 0
	control_msgs.ctrl_V = data.transform.translation.x * 100 * math.sin(3.14159 * t)
	"""
	kp1 = 150
	kp2 = 150
	if i == 0:
		control_msgs.ctrl_W = 0
		control_msgs.ctrl_V = - kp1 * (data.transform.translation.x - 1)
	elif i == 1:
		control_msgs.ctrl_W = 0
		control_msgs.ctrl_V = - kp2 * (data.transform.translation.x - 2)

	# Publishing
	#rospy.loginfo(control_msgs)
	pub[i].publish(control_msgs)

def central():
	# Set up the Subscribers
	sub = []
	for i in range(khep_node_cnt):
		# Automatically subscribes to existing vicon topics corresponding to each khepera
		sub.append(rospy.Subscriber('vicon/k' + ip_num_list[i] + '/k' + ip_num_list[i], TransformStamped, callback, i ))

	# Spin to loop all callback functions
	rospy.spin()


if __name__ == '__main__':
	try:
		central()
	except rospy.ROSInterruptException:
		start = time.time()
		stop_msg = K4_controls()
		stop_msg.ctrl_V = 0
		stop_msg.ctrl_W = 0
		while(time.time() - start < 2):
			for i in range(len(pub)):
				print "stop"
				pub[i].publish(stop_msg)

		#pass