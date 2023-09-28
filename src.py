from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import numpy as np
from gtts import gTTS
import pygame

# Parameters
a = 0
b = 0
c=1
width, height = 1280, 720
gestureThreshold = 300
folderPath = "images"
cameraWindowWidth = 400  # Adjust the desired width of the camera window
cameraWindowHeight = 300  # Adjust the desired height of the camera window

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

# Variables
fingers = None  # Add this line to define the 'fingers' variable
imgList = []
delay = 30
buttonPressed = False
counter = 0
drawMode = False
imgNumber = 0
delayCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

# Get list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

# Color options
colorOptions = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
currentColorIndex = 0

# Initialize Pygame mixer for audio playback
pygame.mixer.init()
pygame.init()

# Load cover image
coverImagePath = "cover/coverpage.jpeg"  # Replace with your cover image path
coverImage = cv2.imread(coverImagePath)

# Set initial state to show cover page
showCoverPage = True

# Show image window switch
showImageWindow = True

def play_audio(text):
    # Save the text as an audio file
    tts = gTTS(text=text, lang="te")
    tts.save("speech.mp3")

    # Load and play the audio file
    pygame.mixer.music.load("speech.mp3")
    pygame.mixer.music.play()


while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Find the hand and its landmarks
    hands, img = detectorHand.findHands(img)  # with draw
    # Draw Gesture Threshold line
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:  # If hand is detected
        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]  # List of 21 Landmark points
        fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold:  # If hand is at the height of the face
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                buttonPressed = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    play_audio("Left")
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                buttonPressed = True
                if imgNumber < len(pathImages) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                    play_audio("Right")
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, colorOptions[currentColorIndex], cv2.FILLED)

        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            print(annotationNumber)
            annotations[annotationNumber].append(indexFinger)
            cv2.circle(imgCurrent, indexFinger, 12, colorOptions[currentColorIndex], cv2.FILLED)
        else:
            annotationStart = False

        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True
                print(annotationNumber)
    else:
        annotationStart = False

    if fingers == [1, 1, 0, 0, 0]:  # Thumb and Index Finger are up
        # Change color index to the next color option
        currentColorIndex = (currentColorIndex + 1) % len(colorOptions)

    if fingers == [0, 1, 1, 1, 1]:
        # Close the window
        buttonPressed = True
        play_audio("Closing the window")
        break
    if fingers == [1, 1, 0, 0, 1] and a == 0:
        play_audio("hi,  i am  hand gesture recognition model ")
        a = 1
    if fingers == [1, 1, 1, 1, 1] and b == 0:
        play_audio("This project is submitted by Akash and Hrushikesh")
        b = 1
    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False
    if fingers==[0,0,0,0,0] and c:
        showCoverPage = False
        c=0
        play_audio("booooooom")
    for i, annotation in enumerate(annotations):
        for j in range(len(annotation)):
            if j != 0:
                cv2.line(imgCurrent, annotation[j - 1], annotation[j], colorOptions[currentColorIndex], 12)

    if showCoverPage :
        imgCurrent = coverImage.copy()
        if not showImageWindow:
            img = np.zeros((cameraWindowHeight, cameraWindowWidth, 3), np.uint8)
    else:
        if not showImageWindow:
            img = np.zeros((cameraWindowHeight, cameraWindowWidth, 3), np.uint8)
        else:
            imgSmall = cv2.resize(img, (ws, hs))
            h, w, _ = imgCurrent.shape
            imgCurrent[0:hs, w - ws: w] = imgSmall

            # Draw color buttons on the slide
            for i, color in enumerate(colorOptions):
                cv2.rectangle(imgCurrent, (10 + i * 60, 10), (60 + i * 60, 60), color, cv2.FILLED)

    cv2.imshow("Slides", imgCurrent)
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == ord('o'):  # Press 'o' to show the original slide
        showCoverPage = False
    elif key == ord('s'):  # Press 's' to toggle image window visibility
        showImageWindow = not showImageWindow
    elif key == ord('q'):
        break

# Release the camera and audio playback resources
cap.release()
pygame.mixer.quit()
cv2.destroyAllWindows()