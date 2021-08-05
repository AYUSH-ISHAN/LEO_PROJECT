#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('leo_drive')
import sys
import rospy
import numpy as np
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
# from capture_image.callback import getLaneCurve
from capture_image import *
#from opencv_files_name import class_of_image_manipulation




class Controller:

	def __init__(self):
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber("/camera/image_raw",Image,self.controlling)
            #self.odom_sub = rospy.Subscriber("/controllers/diff_drive/odom", Twist, queue_size = 10)
            self.motion_pub = rospy.Publisher("/cmd_vel", Twist, queue_size = 10)
            # self.error = error()
            # self.D = differential()
            # self.I = integral()
            # self.P = proportional()
            # self.PID = PID(

	def controlling(self,data):
            try:
                cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
            except CvBridgeError as e:
                print(e)

            rows,cols,channels= cv_image.shape
            # print(rows, cols, channels)   rows = height = 480 and cols = width = 640
            wT = 640
            hT = 480 

            if channels==4 :
                img= cv_image[:,:,0:3]
                
            else:
                img=cv_image
            img= np.flip(img,axis=2)


            curveVal= getLaneCurve(img)
            k = -0.0025
            vel = Twist()
            vel.angular.z = k*curveVal ;
            # sen = 1.3  # SENSITIVITY
            # maxVAl= 0.3 # MAX SPEED
            # if curveVal>maxVAl:curveVal = maxVAl
            # if curveVal<-maxVAl: curveVal =-maxVAl
            # print(curveVal)
            # if curveVal>0:
            #     sen =1.7
            #     if curveVal<0.05: curveVal=0
            # else:
            #     if curveVal>-0.08: curveVal=0

            
            #vel.angular.z = 1;
            vel.linear.x = 2

            self.motion_pub.publish(vel)

            #motor.move(0.20,-curveVal*sen,0.05)  # move is a class defined manually.
            #cv2.waitKey(1)


def main(args):
    rospy.init_node('controller', anonymous=True)
    ic = Controller()
    #   ic.controlling()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    #   cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)






# ic = image_converter()
# rospy.init_node('image_converter', anonymous=True)
# try:
# rospy.spin()
# except KeyboardInterrupt:
# print("Shutting down")
# cv2.destroyAllWindows()

# if __name__== __main__:
#     k = Controller

#     while True:
#         k.controlling

	# def error(self):
	# 	'''this function to calculate the deviation of our car from the 
	# 	line (y = m*x + c) representing the center of road.
	# 	'''
	# 	pass

	# def proportional(self):
	# 	''' this funvtion handels the proportionality part of PID
	# 	'''
	# 	pass

	# def integral(self):
	# 	'''this function handels the integral part 
	# 	'''
	# 	pass

	# def differential(self):
    #    	''' this is the differential part of PID
    #    	'''

	# 	pass

	# def PID(self):
	# 	pass

	# def opencv_trackbars(self):
	# 	''' this function will be used to select the values of P I D coeffecients in form of 
	# 	opencv trackbars (if possible)
	# 	'''
	# 	pass

	
	



