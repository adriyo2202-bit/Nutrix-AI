import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

url: str = "https://cyarpuawppwwnzocorco.supabase.co"
key: str = "sb_publishable_6i2el78jez3trg8Up2xMsw_JI9h_nNr"
supabase: Client = create_client(url, key)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Verify token by getting the user from Supabase using this JWT
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            raise Exception("Supabase auth failed")
        return res.user
    except Exception as e:
        # Fallback to local JWT for development
        try:
            from nutrix_ai.auth import decode_access_token
            payload = decode_access_token(token)
            if payload and payload.get("sub"):
                class MockUser:
                    def __init__(self, email):
                        self.id = "dev_uuid_12345"
                        self.email = email
                return MockUser(payload.get("sub"))
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
