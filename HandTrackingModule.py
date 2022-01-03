from cv2 import cv2 as cv2
import mediapipe as mp
import time
import math


class HandDetector:
    def __init__(self, mode=False, maxhands=2, complexity=1, detectioncon=0.5, trackcon=0.5):
        self.mode = mode
        self.maxhands = maxhands
        self.complexity = complexity
        self.detectioncon = detectioncon
        self.trackcon = trackcon
        self.lmList = list()
        self.tipIds = [4, 8, 12, 16, 20]

        self.pink = (255, 0, 255)
        self.green = (0, 255, 0)
        self.blue = (255, 0, 0)
        self.red = (0, 0, 255)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxhands, self.complexity, self.detectioncon, self.trackcon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLM in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLM, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handnumber=0, draw=True):
        bbox = list()
        xList = list()
        yList = list()

        self.lmList = list()
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handnumber]
            for idx, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([idx, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20), (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)

        return self.lmList, bbox

    def findersUp(self):
        fingers = list()
        # Thumb
        if self.lmList[self.tipIds[0][1]] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 fingers
        for idx in range(1, 5):
            if self.lmList[self.tipIds[idx]][2] < self.lmList[self.tipIds[idx] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        _t1, x1, y1 = self.lmList[p1]
        _t2, x2, y2 = self.lmList[p2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Cria um ponto no meio dos dois dedos

        if draw:
            cv2.circle(img, (x1, y1), 7, self.pink, cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, self.pink, cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), self.green, 2)
            cv2.circle(img, (cx, cy), 7, self.red, cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    pTime = 0
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        if lmList:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (10, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 250), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
