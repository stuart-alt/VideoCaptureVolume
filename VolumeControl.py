import math
import time
from ctypes import cast, POINTER
import HandTrackingModule as htm
from comtypes import CLSCTX_ALL
from cv2 import cv2
from numpy import interp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Cores que serão usadas para visualização
pink = (255, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
red = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)

# Largura e altura da camera
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.HandDetector(detectioncon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

volBar = 200
minVol, maxVol = volRange[0], volRange[1]
volPerc = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if lmList:
        _t1, x1, y1 = lmList[4]
        _t2, x2, y2 = lmList[8]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Cria um ponto no meio dos dois dedos

        cv2.circle(img, (x1, y1), 7, pink, cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, pink, cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), green, 2)
        cv2.circle(img, (cx, cy), 7, red, cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # Hand range: 50-300
        # Vol  range: -74 - 0
        vol = interp(length, [50, 300], [minVol, maxVol])
        volBar = interp(length, [50, 300], [400, 150])
        volPerc = interp(length, [50, 300], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:  # Muda a cor do circulo quando está fechado
            cv2.circle(img, (cx, cy), 7, blue, cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), blue, 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), blue, cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, white, 2)
    cv2.putText(img, f'Vol: {int(volPerc)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, blue, 2)

    cv2.imshow('Img', img)
    cv2.waitKey(1)
