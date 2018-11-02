import uuid
import datetime
from common.database import Database
from models.Place  import Place
from geopy.geocoders import Nominatim

__author__ = 'jetfire'


class Cities(object):
    def __init__(self, city, lat,lon, _id=None):
        self.city = city
        self.lat = lat
        self.lon = lon
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_place(self, place, lat, lon):
        post = Place(city_id=self._id,
                    place=place,
                    lat=lat,
                    lon=lon,
                    cordinates=[(lat,lon)],
                    city=self.city)
        post.save_to_mongo()

    def get_places(self):
        return Place.from_city(self._id)

    def get_places1(self):
        return  Place.from_all_topic(self.city)


    def save_to_mongo(self):
        Database.insert(collection='city',
                        data=self.json())

    def json(self):
        return {
            'city': self.city,
            'lat': self.lat,
            'lon': self.lon,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, city):
        city_data = Database.find_one(collection='city',
                                      query={'city': city})
        return cls(**city_data)

    @classmethod
    def find_by_city(cls, city):
        cities = Database.find(collection='city',
                              query={'city': city})
        print(cities)
        return [cls(**city) for city in cities]

    @staticmethod
    def from_all_cities():
        return [city for city in Database.find(collection='city', query={})]

