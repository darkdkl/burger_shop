from yandex_geocoder import Client
from geopy import distance
from StarBurger.settings import YANDEX_API_KEY


def get_distance(address_from,address_to):
    client = Client(YANDEX_API_KEY)
    coord_from = client.coordinates(address_from)
    coord_to =client.coordinates(address_to)
    return round(distance.distance(coord_from, coord_to).km,2)


