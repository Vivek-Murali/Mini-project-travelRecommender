import uuid
import datetime
from common.database import Database
from models.post import Post

__author__ = 'jetfire'


class Topic(object):
    def __init__(self, username, title, description, author_id, _id=None):
        self.username = username
        self.author_id = author_id
        self.title = title
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_post(self, title, content, date=datetime.datetime.utcnow()):
        post = Post(topic_id=self._id,
                    tittle=title,
                    message=content,
                    username=self.username,
                    date_posted=date)
        post.save_to_mongo()

    def get_posts(self):
        return Post.from_topic(self._id)

    def get_posts1(self):
        return  Post.from_all_topic(self.username)


    def save_to_mongo(self):
        Database.insert(collection='topic',
                        data=self.json())

    def json(self):
        return {
            'username': self.username,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, id):
        blog_data = Database.find_one(collection='topic',
                                      query={'_id': id})
        return cls(**blog_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        topics = Database.find(collection='topic',
                              query={'author_id': author_id})
        return [cls(**topic) for topic in topics]

    @classmethod
    def find_by_username(cls, username):
        topics = Database.find(collection='topic', query={'username': username})
        return [cls(**topic) for topic in topics]
