from common.database import Database

__author__ = 'jetfire'


class List(object):
    def __init__(self, username, title, description):
        self.username = username
        self.title = title
        self.description = description

    @classmethod
    def get_list_by_username(cls, username):
        data = Database.find_one("bucket", {"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def lists(cls, username, title, description):
        liste1 = cls(username, title, description)
        liste1.save_to_mongo()

    @classmethod
    def find_by_username(cls, username):
        topics = Database.find(collection='bucket', query={'username': username})
        return [cls(**lists) for lists in topics]

    @staticmethod
    def from_user_list(username):
        return [list1 for list1 in Database.find(collection='bucket', query={'username': username})]

    def json(self):
        return {
            'username': self.username,
            'title': self.title,
            'description': self.description,
        }

    def save_to_mongo(self):
        Database.insert(collection='bucket', data=self.json())