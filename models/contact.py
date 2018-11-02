from common.database import Database

__author__ = 'jetfire'


class Con(object):
    def __init__(self, username, email, message):
        self.username = username
        self.email = email
        self.message = message

    @classmethod
    def cons(cls, username, email, message):
        con1 = cls(username, email, message)
        con1.save_to_mongo()

    def json(self):
        return {
            'username': self.username,
            'email': self.email,
            'message': self.message,
        }

    def save_to_mongo(self):
        Database.insert(collection='contact', data=self.json())