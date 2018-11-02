from common.database import Database

__author__ = 'jetfire'


class Promotion(object):
    def __init__(self, agencyname, mobile, description):
        self.agencyname = agencyname
        self.mobile = mobile
        self.description = description

    @classmethod
    def promos(cls, agencyname, mobile, description):
        promo1 = cls(agencyname, mobile, description)
        promo1.save_to_mongo()

    @staticmethod
    def from_user_list():
        return [list1 for list1 in Database.find(collection='promo', query={})]

    def json(self):
        return {
            'agencyname': self.agencyname,
            'mobile': self.mobile,
            'description': self.description,
        }

    def save_to_mongo(self):
        Database.insert(collection='promo', data=self.json())