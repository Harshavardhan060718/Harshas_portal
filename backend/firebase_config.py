import os
import glob
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Determine paths for backend directory and root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

# List of potential paths to look for 'firebase-key.json'
paths_to_check = [
    os.path.join(current_dir, "firebase-key.json"),
    os.path.join(root_dir, "firebase-key.json"),
]

KEY_PATH = None
for path in paths_to_check:
    if os.path.exists(path):
        KEY_PATH = path
        break

# Fall back to scanning both directories for any other .json credentials files
if not KEY_PATH:
    json_files = glob.glob(os.path.join(current_dir, "*.json")) + glob.glob(os.path.join(root_dir, "*.json"))
    # Filter out common project configurations like package.json or tsconfig.json
    json_files = [f for f in json_files if not os.path.basename(f).startswith("package") and not os.path.basename(f).startswith("tsconfig")]
    if json_files:
        KEY_PATH = json_files[0]

# Final check
if not KEY_PATH:
    raise FileNotFoundError(
        f"\n[ERROR] Firebase service account key JSON file not found inside: {current_dir} or {root_dir}\n"
        "To fix this, go to Firebase Console > Settings > Service Accounts,\n"
        "click 'Generate new private key', and upload the JSON file."
    )

print(f"[INFO] Initializing Firebase using key file: {os.path.basename(KEY_PATH)}")

# Initialize Firebase Admin App
cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)

# Initialize Firestore DB client
db = firestore.client()
