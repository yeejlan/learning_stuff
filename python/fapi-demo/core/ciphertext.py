import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from nacl.exceptions import CryptoError
from nacl.secret import Aead
from nacl.utils import random
from config import getConfig

config = getConfig()

class CiphertextException(Exception):
    pass

class Ciphertext:

    def getKey(self) -> bytes:
        return self._get_config_value('CIPHERTEXT_SECRET')

    def get2FAKey(self) -> bytes:
        return self._get_config_value('CIPHERTEXT_2FA')

    def _get_config_value(self, key) -> bytes:
        value = config.get(key)
        if not value:
            raise CiphertextException(f"{key} not available.")
        return bytes.fromhex(value)

    def encrypt(self, key, message):
        secret_box = Aead(key)
        encrypted_message = secret_box.encrypt(message.encode())
        return encrypted_message.hex()

    def decrypt(self, key, encrypted_message):
        try:
            encrypted_message = bytes.fromhex(encrypted_message)
            secret_box = Aead(key)
            decrypted_message = secret_box.decrypt(encrypted_message)
            return decrypted_message.decode()
        except (CryptoError, ValueError):
            return ''

    def generate_key(self) -> str:
        key = random(32)
        return key.hex()


if __name__ == "__main__":
    import asyncio

    async def main():
        ciphertext = Ciphertext()

        key = ciphertext.generate_key()
        print(key)

        key = ciphertext.getKey()
        message = 'this is my testig message~'
        encoded_message = ciphertext.encrypt(key, message)
        print(len(encoded_message))
        print(encoded_message)
        decoded_message = ciphertext.decrypt(key, encoded_message)
        print(decoded_message)

    asyncio.run(main())    