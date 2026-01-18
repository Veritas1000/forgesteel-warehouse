
import logging

from cryptography.fernet import Fernet, MultiFernet

log = logging.getLogger(__name__)

class Crypt(object):
    _encoding = 'utf-8'

    def __init__(self, key):
        keys = map(lambda s: Fernet(s.encode(self._encoding)), key.split(';'))
        self.fernet = MultiFernet(keys)

    def encrypt(self, value):
        return self.fernet.encrypt(value.encode(self._encoding)).decode(self._encoding)
    
    def decrypt(self, token):
        return self.fernet.decrypt(token).decode(self._encoding)
    
    def rotate(self, token):
        return self.fernet.rotate(token).decode(self._encoding)
    