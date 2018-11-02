import datetime
import uuid
from flask import session
from common.database import Database


class Place(object):
    def __init__(self, place, city, lat,lon, _id=None):
        self.place = place
        self.city = city
        self.lat = lat
        self.lon = lon
        self.cordinates = (lat,lon)
        self._id = uuid.uuid4().int>>64 if _id is None else _id

    @classmethod
    def get_place_by_id(cls, _id):
        data = Database.find_one("place", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_place_by_placename(cls, place):
        data = Database.find_one("place", {"place":place})
        if data is not None:
            return cls(**data)

    @classmethod
    def from_mongo(cls, id):
        place_data = Database.find_one(collection='place', query={'_id': id})
        return cls(**place_data)

    @staticmethod
    def from_all_places():
        return [place for place in Database.find(collection='place', query={})]

    @staticmethod
    def from_city_place(city):
        return [place for place in Database.find(collection='place', query={'city':city})]

    def json(self):
        return {
            '_id': self._id,
            'Place': self.place,
            'lat': self.lat,
            'lon': self.lon,
            'city':self.city
        }

    def save_to_mongo(self):
        Database.insert(collection='post',
                        data=self.json())
