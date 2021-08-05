
from __future__ import print_function

import numpy as np
import cv2

def masking(img):
      lower_road = np.array([0,0,0])        
      upper_road = np.array([100,100,100])   

      mask = cv2.inRange(img, lower_road, upper_road)
      return mask 

def warpImg(img, points, w, h, inv = False):
  pts1 = np.float32(points)
  pts2 = np.float32([[0,0], [w,0], [0,h], [w,h]])

  matrix = cv2.getPerspectiveTransform(pts1, pts2)
  imgWarp = cv2.warpPerspective(img, matrix, (w,h))

  return imgWarp


def getHistogram(img, display=False, minPer=0.1, region=4):

  if region == 1:
      histValues = np.sum(img, axis=0)   ## sum of all in a column

  else:
      histValues = np.sum(img[3*(img.shape[0]//region):,:], axis=0)

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
  point = np.float32([(220,200),(420,200),(15,380),(625,380)])
  imgWarp = warpImg(mask_img, point, 640, 480)
  middlePoint = getHistogram(imgWarp,minPer=0.5)
  curveAveragePoint = getHistogram(imgWarp,False, 0.9,1)
  curveRaw = curveAveragePoint-middlePoint

  curveList = []
  curveList.append(curveRaw)
  if len(curveList) > 10:
      curveList.pop(0)
  curve = int(sum(curveList)/len(curveList))
  imz= cv2.resize(imgWarp,(250,250))
  cv2.imshow("ss",imz)
  cv2.waitKey(1)
  return curve




