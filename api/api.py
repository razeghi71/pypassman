from common.db import App, SavedInfo
from Crypto.Cipher import AES
from common.patterns import Singleton
from common.app import SingleApp
import hashlib
import base64


BLOCK_SIZE = 16

PADDING = '{'

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)


class API(Singleton):

    def set_key(self, key):
        self.cypher = AES.new( pad(key) )

    def register_app(self, new_app):
        app = App.select().where(App.executable == new_app.executable)
        if not app.exists():
            app = App()
            app.executable = new_app.executable 
            app.exec_hash = new_app.exec_hash
            app.save()
            return app.id
        return -1

    def update_app(self, updated_app):
        app = App.get(App.executable == updated_app.executable)
        if app:
            app.executable = updated_app.executable
            app.exec_hash = updated_app.exec_hash
            app.save()
            return app.id
        return -1

    def save_password(self, connected_app, username, password):
        app = App.get(App.executable == connected_app.executable)
        if app:
            save_info = SavedInfo()
            save_info.app = app
            save_info.username = username
            save_info.password = EncodeAES(self.cypher,password)
            save_info.save()
            return save_info.id
        return -1

    def get_password(self, connected_app ,saved_id):
        saved = SavedInfo.select().where(SavedInfo.id == saved_id)
        app = App.get(App.executable == connected_app.executable)
        if saved.exists() and app == saved[0].app:
            return saved[0].id, saved[0].username, DecodeAES(self.cypher, saved[0].password)
        return -1, -1, -1
