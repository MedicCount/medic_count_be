import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

cred = credentials.Certificate('app/serviceAccount.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'medicine-proj.appspot.com'
})
print("🔥 Connected to Firestore")

f_store = firestore.client()
authen = auth
storage = storage
timestamp = firestore.SERVER_TIMESTAMP