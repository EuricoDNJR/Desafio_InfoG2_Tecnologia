import os

import pyrebase
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

load_dotenv()


def initialize_firebase():
    if not firebase_admin._apps:
        firebase_cert_dict = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
        }

        cred = credentials.Certificate(firebase_cert_dict)
        firebase_admin.initialize_app(cred)

    apiKey = os.getenv("FIREBASE_API_KEY")
    authDomain = os.getenv("FIREBASE_AUTH_DOMAIN")
    projectId = os.getenv("FIREBASE_PROJECT_ID")
    storageBucket = os.getenv("FIREBASE_STORAGE_BUCKET")
    messagingSenderId = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    appId = os.getenv("FIREBASE_APP_ID")
    measurementId = os.getenv("FIREBASE_MEASUREMENT_ID")

    firebaseConfig = {
        "apiKey": apiKey,
        "authDomain": authDomain,
        "projectId": projectId,
        "storageBucket": storageBucket,
        "messagingSenderId": messagingSenderId,
        "appId": appId,
        "measurementId": measurementId,
        "databaseURL": "",
    }

    firebase = pyrebase.initialize_app(firebaseConfig)
    return firebase
