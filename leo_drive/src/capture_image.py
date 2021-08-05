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

class image_converter:

  ## read HArdware Implementation part in Lane Detection-Image Processing to get an idea of fhow we are going to connect 
  # this opencv work with motion of bot.


  def __init__(self):
    #self.image_pub = rospy.Publisher("image_topic_2",Image)

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/camera/image_raw",Image,self.callback)
    self.odom_sub = rospy.Subscriber("/controllers/diff_drive/odom", Twist, queue_size = 10)
    self.motion_pub = rospy.Publisher("/cmd_vel", Twist, queue_size = 10)


  def callback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
    except CvBridgeError as e:
      print(e)

    (rows,cols,channels) = cv_image.shape
    # print(rows, cols, channels)   rows = height = 480 and cols = width = 640

    wT = 640  # cols
    hT = 480  # rows

    if channels==4 :
    	img= cv_image[:,:,0:3]
    	
    else:
    	img=cv_image
    img= np.flip(img,axis=2)

    # masking done to separate out road from otehr enviroment

    def masking(img):
      lower_road = np.array([0,0,0])        
      upper_road = np.array([100,100,100])   
      ## blurring the image - no_need  

      mask = cv2.inRange(img, lower_road, upper_road)
      return mask 

    def nothing(a):
      pass

  ## consecutive two functions are for creating trackbars to adjust our dimensions..
  ## we can remove it as we are not using it

  ## the arguments is some cases are 480 and 640, actually rows = 480 and columns = 640 of out leo camera output.

    def initializeTrackbars(initialTracebarVals, wT=640, hT=480):
      cv2.namedWindow("Trackbars")
      cv2.resizeWindow("Trackbars", 480, 640)
      cv2.createTrackbar("Width Top", "Trackbars", initialTracebarVals[0], wT//2, nothing)
      cv2.createTrackbar("Height Top", "Trackbars", initialTracebarVals[1], hT, nothing)
      cv2.createTrackbar("Width Bottom", "Trackbars", initialTracebarVals[2], wT//2, nothing)
      cv2.createTrackbar("Height Bottom", "Trackbars", initialTracebarVals[3], hT, nothing)

    def valTrackbars(wT=640, hT=480):
      widthTop = cv2.getTrackbarPos("Width Top", "Trackbars")
      heightTop = cv2.getTrackbarPos("Height Top", "Trackbars")
      widthBottom = cv2.getTrackbarPos("Width Bottom", "Trackbars")
      heightBottom = cv2.getTrackbarPos("Height Bottom", "Trackbars")
      points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
                        (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
      
      return points

    intialTracbarVals = [110,208,0,480]
    initializeTrackbars(intialTracbarVals)

    points = valTrackbars()

    # doing Warping of image to get the Bird Eye View :

    def warpImg(img, points, w, h, inv = False):
      img = masking(img)
      pts1 = np.float32(points)
      pts2 = np.float32([[0,0], [w,0], [0,h], [w,h]])
      if inv:
        matrix = cv2.getPerspectiveTransform(pts2, pts1)
      else:
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
      imgWarp = cv2.warpPerspective(img, matrix, (w,h))

      return imgWarp

    #imgWarp = warpImg(masking(cv_image), points, cols, rows)

    def getHistogram(img, display, minVal=0.1, region=4):

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

      middlePoint = getHistogram(imgWarp,minPer=0.5)
      curveAveragePoint,imgHist = getHistogram(imgWarp, True, 0.9,1)
      curveRaw = curveAveragePoint-middlePoint

      curveList = []

      curveList.append(curveRaw)
      if len(curveList) > avgVal:
          curveList.pop(0)
      curve = int(sum(curveList)/len(curveList))

      def getLaneCurve(imgWarp, display):

          print("I am in getLaneCurve")

          if display != 0:
               imgInvWarp = warpImg(imgWarp, points, wT, hT,inv = True)
               imgInvWarp = cv2.cvtColor(imgInvWarp,cv2.COLOR_GRAY2BGR)
               imgInvWarp[0:hT//3,0:wT] = 0,0,0
               imgLaneColor = np.zeros_like(img)
               imgLaneColor[:] = 0, 255, 0
               imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
               imgResult = cv2.addWeighted(imgResult,1,imgLaneColor,1,0)

               midY = 320 # this is the mid value of number of columns. # previos value was =  450

               cv2.putText(imgResult,str(curve),(wT//2-80,85),cv2.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
               cv2.line(imgResult,(wT//2,midY),(wT//2+(curve*3),midY),(255,0,255),5)
               cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY-25), (wT // 2 + (curve * 3), midY+25), (0, 255, 0), 5)
               for x in range(-30, 30):
                   w = wT // 20
                   cv2.line(imgResult, (w * x + int(curve//50 ), midY-10),
                            (w * x + int(curve//50 ), midY+10), (0, 0, 255), 2)
               fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
               cv2.putText(imgResult, 'FPS '+str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230,50,50), 3);

          if display == 2:
               imgStacked = stackImages(0.7,([img,imgWarpPoints,imgWarp], [imgHist,imgLaneColor,imgResult]))
               cv2.imshow('ImageStack',imgStacked)
               cv2.waitKey(3)

          elif display == 1:

               print("I am in display = 1")

               cv2.imshow('Resutlt',imgResult)
               cv2.waitKey(3)


      def stackImages(scale,imgArray):
          rows = len(imgArray)
          cols = len(imgArray[0])
          rowsAvailable = isinstance(imgArray[0], list)
          width = imgArray[0][0].shape[1]
          height = imgArray[0][0].shape[0]
          if rowsAvailable:
              for x in range ( 0, rows):
                  for y in range(0, cols):
                      if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                          imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                      else:
                          imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                      if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
              imageBlank = np.zeros((height, width, 3), np.uint8)
              hor = [imageBlank]*rows
              hor_con = [imageBlank]*rows
              for x in range(0, rows):
                  hor[x] = np.hstack(imgArray[x])
              ver = np.vstack(hor)
          else:
              for x in range(0, rows):
                  if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                      imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                  else:
                      imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
                  if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
              hor= np.hstack(imgArray)
              ver = hor
          return ver

 ###  reason is not known but not able to call the function getLanceCurve..

      # display = 1
      # curve_val = getLaneCurve(display)

    #cv2.imshow("warp_image", imgWarp)
    cv2.imshow("Image window", img)
    cv2.imshow("mask", masking(img))
    # cv2.imshow("histograms", img_Hist)
    cv2.waitKey(3)
    

##  below are the commands to move leo car... these commands will be needed to check the functioning of code
## at turns.
  
    velocity = Twist()

    velocity.linear.x = 10
    self.motion_pub.publish(velocity)
    
    # try:
    #   self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "passthrough"))
    # except CvBridgeError as e:
    #   print(e)

def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
