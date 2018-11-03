import datetime
import uuid
from flask import session
from common.database import Database
from flask_pymongo import PyMongo, pymongo


class Rating(object):
    def __init__(self, place_id,user_id,avg_rating,no_of_rating ,user_rating, _id=None):
        self.place_id = place_id
        self.user_id = user_id
        self.avg_rating = avg_rating
        self.no_of_rating = no_of_rating
        self.user_rating = user_rating
        self._id = uuid.uuid4().hex  if _id is None else _id

    @classmethod
    def get_post_by_place(cls, place):
        data = Database.find_one("place", {"place_id":place})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_post_by_place_id(cls, place_id):
        data = Database.find_one("place", {"place_id":place_id})
        if data is not None:
            return cls(**data)

    @classmethod
    def post_chirp(cls, message, username, tag, date_posted):
        username = session['username']
        picture = session['picture']
        Database.insert("post", {"message": message, "username": username, "tag": tag, "picture": picture, "date_posted": date_posted})
        session['username'] = username
        return True

    @classmethod
    def show_chrip(cls):
        posts = Database.find('post', {})
        print(posts)
        return posts

    @classmethod
    def lists(cls, place_id, user_id, avg_rating, no_of_rating,user_ratiing):
        liste1 = cls(place_id,user_id,avg_rating,no_of_rating,user_ratiing)
        liste1.save_to_mongo()

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection='post', query={'_id': id})
        return cls(**post_data)

    @staticmethod
    def from_place_id(place):
        return [post for post in Database.find(collection='place', query={'Place':place})]

    @staticmethod
    def from_user_topic(username):
        return [post for post in Database.find(collection='post', query={'username':username}).sort('date_posted', pymongo.DESCENDING)]

    @staticmethod
    def from_topic(_id):
        return [post for post in Database.find(collection='post', query={'topic_id': _id}).sort('date_posted', pymongo.DESCENDING)]

    def json(self):
        return {
            '_id': self._id,
            'place_id': self.place_id,
            'avg_rating': self.avg_rating,
            'no_of_rating': self.no_of_rating,
            'user_id':self.user_id,
            'user_rating': self.user_rating,
        }

    def save_to_mongo(self):
        Database.insert(collection='rating_place',
                        data=self.json())
