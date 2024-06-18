#! /usr/bin/env python

import math
import rospy
import httpx
import json
from sensor_msgs.msg import LaserScan
import sensor_msgs.msg

rev_scan = LaserScan()

def callback(msg):

    global count
    if count != 10:
        count+=1
    else:
        count=0
        print("1s")
        
        # #print(len(msg.ranges)) len is 2019 from 0-360
        # req_range = rev_scan.msg.ranges[0:72]
        #print(len(msg.ranges))
        addr = "http://192.168.100.209/json"
        x_array = []
        y_array = []
        clear_data = {"seg":{"i":[0,150,"000000"]}}
        # json_data = json.loads(clear_data)
        # print(json_data)
        #httpx.post(addr, json=clear_data)
        for i in range(len(msg.ranges)):
            if(math.isinf(msg.ranges[i])):
                pass
            else:
                theta = math.pi * i / 380
                # print(msg.ranges[i])
                x = msg.ranges[i] * math.sin(theta)
                y = msg.ranges[i] * math.cos(theta)
                if x < 0.8 and x > -0.8 and y > 0 and y < 1.2:
                    x_array.append(x)
                    y_array.append(y)
        if (len(x_array) != 0):
            global left_x
            global right_x
            middle_x = round(sum(x_array)/len(x_array) * 60)
            #print(sum(x_array)/len(x_array))
            if middle_x - 15 > -60:
                current_left_x = middle_x - 15
            else:
                current_left_x = -60

            if middle_x + 15 < 60:
                current_right_x = middle_x + 15
            else:
                current_right_x = 60

            current_left_x = current_left_x + 60
            current_right_x = current_right_x + 60
            if current_left_x < left_x:
                pass
            else:
                data = {"seg":{"i":[left_x,current_left_x,"000000"]}}
                httpx.post(addr, json=data)
            if current_right_x < right_x:
                data = {"seg":{"i":[current_right_x,right_x,"000000"]}}
                httpx.post(addr, json=data)
            else:
                pass
            data = {"seg":{"i":[current_left_x,current_right_x,"FFFFFF"]}}
            left_x = current_left_x
            right_x = current_right_x
            # print(left_x)
            # print(right_x)
            # json_data = json.loads(data)
            httpx.post(addr, json=data)

    
def listener():
    rospy.init_node('revised_scan', anonymous=True)
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()

if __name__ == '__main__':
    count = 0
    left_x = 0
    right_x = 0
    listener()