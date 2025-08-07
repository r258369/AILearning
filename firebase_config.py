import os
import json
from firebase_admin import credentials

# Read the JSON string from environment variable
firebase_creds_json = os.environ.get("FIREBASE_ADMIN_CREDENTIALS")  # use your actual env var name here

if not firebase_creds_json:
    raise Exception("FIREBASE_ADMIN_CREDENTIALS_JSON environment variable not set.")

cred_dict = json.loads(firebase_creds_json)  # parse JSON string to dict

cred = credentials.Certificate(cred_dict)
