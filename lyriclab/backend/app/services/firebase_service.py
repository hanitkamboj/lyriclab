import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from app.config import FirebaseConfig
import json

cred_dict = {
    "type": "service_account",
    "project_id": FirebaseConfig.project_id,
    "private_key_id": None,
    "private_key": None,
    "client_email": None,
    "client_id": None,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

class FirebaseService:
    _initialized = False
    _db = None

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': FirebaseConfig.project_id,
                'storageBucket': FirebaseConfig.storage_bucket,
            })
            cls._initialized = True
        except:
            try:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {
                    'projectId': FirebaseConfig.project_id,
                    'storageBucket': FirebaseConfig.storage_bucket,
                })
                cls._initialized = True
            except:
                pass

    @classmethod
    def get_db(cls):
        if not cls._initialized:
            cls.initialize()
        if not cls._db:
            try:
                cls._db = firestore.client()
            except:
                pass
        return cls._db

    @classmethod
    def verify_token(cls, id_token: str) -> dict:
        try:
            decoded = auth.verify_id_token(id_token)
            return decoded
        except Exception as e:
            raise Exception(f"Firebase auth failed: {e}")

    @classmethod
    def create_user(cls, email: str, password: str) -> dict:
        try:
            user = auth.create_user(email=email, password=password)
            return {"uid": user.uid, "email": user.email}
        except Exception as e:
            raise Exception(f"User creation failed: {e}")

    @classmethod
    def get_user(cls, uid: str) -> dict:
        try:
            user = auth.get_user(uid)
            return {"uid": user.uid, "email": user.email, "display_name": user.display_name}
        except Exception as e:
            raise Exception(f"Get user failed: {e}")
