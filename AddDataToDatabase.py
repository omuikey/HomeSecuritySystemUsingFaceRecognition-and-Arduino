
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' :"https://facehomesecurityrealtime-default-rtdb.firebaseio.com/"
})

ref = db.reference('Members')

data = {
    "001":
        {
            "Name": "Rushikesh Unde",
            "last_entry_time":"2022-05-20 00:54:34"

        },
    "002":
        {
            "Name": "Bhushan Sadmake",
            "last_entry_time":"2022-05-20 00:54:34"

        }
}

for key,value in data.items():
    ref.child(key).set(value)

