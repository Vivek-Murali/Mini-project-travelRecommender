import uuid
from flask import session
from common.database import Database
from models.topic import Topic
import pandas as pd
import pymongo
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer


class Food(object):
    def __init__(self, Dishes, Descrptions, Kind, _id=None):
        self.place = Dishes
        self.city = Descrptions
        self.lat = Kind
        self._id = uuid.uuid4().int>>64 if _id is None else _id

    @classmethod
    def get_food_by_foodname(cls, place):
        data = Database.find_one("place", {"place": place})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_food_by_id(cls, _id):
        data = Database.find_one("place", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def food_show():
        return [food for food in Database.find(collection='food', query={})]

    @staticmethod
    def recommend(index):
        food_vec = TfidfVectorizer(stop_words='english')
        for food in Database.find(collection='food', query={}):
            food1 = Database.find(collection='food',query={})
            df = pd.DataFrame(list(food1))

        df['Descrptions'] = df['Descrptions'].fillna('')
        food_td_mat = food_vec.fit_transform(df['Descrptions'])
        cos_sim = linear_kernel(food_td_mat, food_td_mat)
        indiecs = pd.Series(df['Dishes'].index)
        id = indiecs[index]
        sim_score = list(enumerate(cos_sim[id]))
        sim_score = sorted(sim_score, key=lambda x: x[1], reverse=True)
        sim_score = sim_score[1:11]
        food_index = [i[0] for i in sim_score]
        return df.iloc[food_index]