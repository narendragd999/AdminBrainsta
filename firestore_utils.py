import firebase_admin
from firebase_admin import credentials, firestore
import os
from settings import FIREBASE_CRED

if not os.path.exists(FIREBASE_CRED): 
    raise FileNotFoundError("❌ serviceAccount.json not found")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED)
    firebase_admin.initialize_app(cred)

db = firestore.client()
