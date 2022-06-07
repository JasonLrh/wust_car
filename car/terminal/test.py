import cv2 as cv
import numpy as np

size = (240,320)
img = cv.merge([np.zeros(size,np.uint8),np.zeros(size,np.uint8),np.zeros(size,np.uint8)])
cv.imshow("te",img)
cv.waitKey(1000)