from matplotlib import pyplot as plt
import cv2
import numpy as np

w=2000
h=1100
pts1=np.float32([[33,1133],[4472,297],[1111,2959],[4345,2211]])
pts2=np.float32([[0,0],[w,0],[0,h],[w,h]])
M=cv2.getPerspectiveTransform(pts1,pts2)
print(M)

img=cv2.imread('pc.jpg')
dst=cv2.warpPerspective(img,M,(w,h))
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
dst = cv2.cvtColor(dst, cv2.COLOR_RGB2BGR)
plt.subplot(121),plt.imshow(img),plt.title('Input')
plt.subplot(122),plt.imshow(dst),plt.title('Output')
plt.show()

