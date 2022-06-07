import cv2 as cv
# fore = cv.VideoWriter_fourcc(*'XVID')
# out = cv.VideoWriter('output.mkv', fore , 30, (160, 120))

cap = cv.VideoCapture("output.mkv")

ret, frame = cap.read()
while frame is not None:
    ret, frame = cap.read()
    cv.imshow("win",frame)
    cv.waitKey(1)


cap.release()