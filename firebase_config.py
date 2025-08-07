# firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("FIREBASE_ADMIN_CREDENTIALS")

# Initialize Firebase with storage bucket configuration
firebase_admin.initialize_app(cred, {
    'storageBucket': 'elearning-8634a.appspot.com'
})

db = firestore.client()
