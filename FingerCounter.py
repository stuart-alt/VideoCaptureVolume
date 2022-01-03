from cv2 import cv2 as cv2
import time
import os
import HandTrackingModule as htm

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)

folderPath = "FingerImages"
myList = os.listdir(folderPath)
overlayList = list()
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')

    overlayList.append(image)

print(len(overlayList))

pTime = 0
detector = htm.HandDetector(detectioncon=0.75, maxhands=1)
tipIds = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)
    if lmlist:
        fingers = list()
        # Checks the thumb
        if lmlist[tipIds[0]][1] > lmlist[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Checks the other 4 fingers
        for idx in range(1, 5):
            if lmlist[tipIds[idx]][2] < lmlist[tipIds[idx] - 2][2]:
                fingers.append(1)  # Se estiver aberto, append 1
            else:
                fingers.append(0)  # Se estiver fechado, append 0
        totalFingers = fingers.count(1)
        print(totalFingers)

        h, w, c = overlayList[0].shape  # Isso vai pegar o tamanho da imagem
        img[0:h, 0:w] = overlayList[totalFingers - 1]

        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (500, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
