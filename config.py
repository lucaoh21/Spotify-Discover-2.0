import os

class Config(object):
    SECRET_KEY = b'\x1e\x10\x81v\x00\x06\x7f\x00<Q\xa0\xb3\xe0\xbd,\xf5'
    client_id = ''
    #os.environ.get('SECRET_KEY') or 'my-super-powerful-unbreakable-key'