import json
import time
from typing import Optional

from pydantic import Field
from core.ciphertext import Ciphertext
from core.config import getConfig
from core.core_model import CoreModel


config = getConfig()

class AccessToken(CoreModel):
    i: int = Field(..., gt = 0, description = 'user_id')
    r: str = Field(..., description = 'role')
    e: int = Field(..., gt = 10000, description =' expire_at')

def _create_access_token(data: dict) -> str:
    ciphertext = Ciphertext()
    key = ciphertext.getKey()
    encoded_message = ciphertext.encrypt(key, json.dumps(data))
    return encoded_message


def _verify_access_token(encoded_message: str) -> dict:
    ciphertext = Ciphertext()
    key = ciphertext.getKey()    
    try:
        decoded_message = ciphertext.decrypt(key, encoded_message)
        data = json.loads(decoded_message)
        return data
    except Exception:
        return {}

def verifyAccessToken(encoded_message: str) -> Optional['AccessToken']:
    data = _verify_access_token(encoded_message)
    if not data:
        return None
    if 'i' not in data or data['i'] < 1:
        return None
    if 'r' not in data or not data['r']:
        return None
    if 'e' not in data or data['e'] < int(time.time()):
        return None

    return AccessToken(**data)


def createAccessToken(user_id: int, role: str = 'user', ex = 86400) -> str:
    profile = {
        'i': user_id, 
        'r': role,
        'e': int(time.time()) + ex,
    }
    token = _create_access_token(profile)
    return token


#depends 
def ensureValidAccessKey():
    pass



if __name__ == "__main__":

    token = createAccessToken(6648244)
    print(f'token(len:{len(token)}) = {token})')
    profile = verifyAccessToken(token)
    print(profile)