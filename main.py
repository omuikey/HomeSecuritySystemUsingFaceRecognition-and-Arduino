import os
import time
import pickle
import face_recognition
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import  storage
from datetime import datetime
from cvzone.SerialModule import SerialObject



cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facehomesecurityrealtime-default-rtdb.firebaseio.com/",
    'storageBucket': "facehomesecurityrealtime.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, homeIds = encodeListKnownWithIds
print("Encoded File Loaded")

modeType = 0
counter = 0
id =-1
imghome = []
ard = SerialObject('COM3')
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                id = homeIds[matchIndex]
                # print(id)
                if counter == 0:
                    counter = 1
                    modeType = 1
            else:
                #print("not matched")
                ard.sendData([0])

        if counter != 0:

            if counter == 1:

                # Get data
                homeInfo = db.reference(f'Members/{id}').get()
                # print(homeInfo)
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imghome = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                datetimeObject = datetime.strptime(homeInfo['last_entry_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                ard.sendData([1])
                            #print(secondsElapsed)
                if secondsElapsed > 15:
                    ref = db.reference(f'Members/{id}')
                    ref.child('last_entry_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    time.sleep(2)
                    modeType = 4
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 5 < counter < 10:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 5:


                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(homeInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(homeInfo['Name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imghome

                counter += 1

                if counter >= 10:
                    counter = 0
                    modeType = 0
                    homeInfo = []
                    imghome = []
                    ard.sendData([0])
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            else:
                modeType = 0
                counter = 0
                #print("not matched")
                # cv2.imshow("Webcam", img)


        cv2.imshow("Home security", imgBackground)
        cv2.waitKey(1)