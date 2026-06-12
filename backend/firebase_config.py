import os
import glob
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Determine absolute path to the backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Look for the standard name 'firebase-key.json'
KEY_PATH = os.path.join(current_dir, "firebase-key.json")

# 2. Fall back to scanning the folder for any other downloaded credentials .json file
if not os.path.exists(KEY_PATH):
    json_files = glob.glob(os.path.join(current_dir, "*.json"))
    if json_files:
        # Use the first JSON file available in the folder
        KEY_PATH = json_files[0]

# Final check
if not os.path.exists(KEY_PATH):
    raise FileNotFoundError(
        f"\n[ERROR] Firebase service account key JSON file not found inside: {current_dir}\n"
        "To fix this, go to Firebase Console > Settings > Service Accounts,\n"
        "click 'Generate new private key', and download the JSON file into the backend folder."
    )

print(f"[INFO] Initializing Firebase using key file: {os.path.basename(KEY_PATH)}")

# Initialize Firebase Admin App
cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)

# Initialize Firestore DB client
db = firestore.client()
