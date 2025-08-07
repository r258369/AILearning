import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Read the JSON string from environment variable
firebase_creds_json = os.environ.get("FIREBASE_ADMIN_CREDENTIALS")  # use your actual env var name here

if not firebase_creds_json:
    raise Exception("FIREBASE_ADMIN_CREDENTIALS_JSON environment variable not set.")

cred_dict = json.loads(firebase_creds_json)  # parse JSON string to dict

cred = credentials.Certificate(cred_dict)
# Initialize app if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
