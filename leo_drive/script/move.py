#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import random
import math

import numpy as np
import cv2

def masking(img):
      lower_road = np.array([0,0,0])        
      upper_road = np.array([100,100,100])   
      ## blurring the image - no_need  

      mask = cv2.inRange(img, lower_road, upper_road)
      return mask 

def warpImg(img, points, w, h, inv = False):
  pts1 = np.float32(points)
  pts2 = np.float32([[0,0], [w,0], [0,h], [w,h]])

  matrix = cv2.getPerspectiveTransform(pts1, pts2)
  imgWarp = cv2.warpPerspective(img, matrix, (w,h))

  return imgWarp


def getHistogram(img, display, minPer=0.1, region=4):

  if region == 1:
      histValues = np.sum(img, axis=0)   ## sum of all in a column

  else:
      histValues = np.sum(img[img.shape[0]//region:,:], axis=0)

  maxValue = np.max(histValues)   # FIND THE MAX VALUE
  minValue = minPer*maxValue  ## we need to specify this parameter

  indexArray = np.where(histValues >= minValue) # this gives all indices with min value or above.
  basePoint = int(np.average(indexArray)) # average all max indices values.

  if display:
    imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    for x, intensity in enumerate(histValues):
      # print(intensity)
      if intensity > minValue:color=(255,0,255)
      else: color=(0,0,255)

      cv2.line(imgHist, (x, img.shape[0]-(intensity//255//region)), color, 1)

    cv2.circle(imgHist, (basePoint, img.shape[0]), 20, (0, 255, 255), cv2.FILLED)

    if region ==1:
        histValues = np.sum(img, axis=0)
    else :
        histValues = np.sum(img[img.shape[0]//region:,:], axis=0)

    return basePoint,imgHist
  return basePoint



def getLaneCurve(img):
  mask_img = masking(img)
  point = np.float32([(210,198),(440,200),(15,300),(630,300)])
  imgWarp = warpImg(masking(cv_image), points, 535, 400)
  










def main():
    rate = rospy.Rate(10) # 10hz
    # lpos = 0
    # rpos = 0
    # cent_x = rospy.Subscriber("/car_centroid_x", Float64)
    # cent_y = rospy.Subscriber("/car_centroid_y", Float64)
    cmd_vel =  rospy.Publisher("/cmd_vel", Twist, queue_size = 10)


    # left_pub = rospy.Publisher("/bot/left_wheel_controller/command",
    #                                         Float64, queue_size=10)
    # right_pub = rospy.Publisher("/bot/right_wheel_controller/command",
    #                                         Float64, queue_size=10)
    while not rospy.is_shutdown():

        # lpos += 2.0
        # rpos += 2.0
        # # if random.randint(0, 4) != 0:
        # left_pub.publish(lpos)
        # # if random.randint(0, 4) != 0:
        # right_pub.publish(rposs)

        vel = Twist()
        #vel.angular.z = 1;
        vel.linear.x = 2
        # vel_lin

        cmd_vel.publish(vel)

        rate.sleep()

if __name__ == '__main__':
    rospy.init_node("move_node", anonymous=True)
    try:
        main()
    except rospy.ROSInterruptException:
        pass
