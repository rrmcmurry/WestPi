import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    _, frame = cap.read()


    # convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # upper and lower HSV values
    lower_color = np.array([168,100,100]) 
    upper_color = np.array([179,255,255])

    # Create a mask
    mask = cv2.inRange(hsv, lower_color, upper_color)


    # Remove some of the noise
    kernel = np.ones((7,7),np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # res = cv2.bitwise_and(frame,frame, mask= opening)

    # Find shapes within the clean image
    contours,_ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest shape and draw a rectangle around it
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        if w > 50:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)


    # Show the results
    cv2.imshow('Original',frame)
    #cv2.imshow('Res',res)


    # Wait for escape key
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
