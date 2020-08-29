from yandex_geocoder import Client
from geopy import distance
from functools import reduce
from StarBurger.settings import YANDEX_API_KEY
from yandex_geocoder.exceptions import InvalidKey, NothingFound
from collections import OrderedDict
from django.core.cache import cache


def get_distance(address_from, address_to, order_id):
    client = Client(YANDEX_API_KEY)
    coord_from = cache.get(f'{order_id}_coord_from')
    coord_to = cache.get(f'{order_id}_coord_to')
    if not coord_from:
        coord_from = client.coordinates(address_from)
        cache.set(f'{order_id}_coord_from', coord_from, 100)
    if not coord_to:
        coord_to = client.coordinates(address_to)
        cache.set(f'{order_id}_coord_to', coord_to, 100)
    dist = cache.get(f'{order_id}_distance')
    if not dist:
        dist = round(distance.distance(coord_from, coord_to).km, 2)
        cache.set(f'{order_id}_distance', dist, 100)
    return dist

# def get_distance(address_from, address_to, order_id):
#     client = Client(YANDEX_API_KEY)
#     coord_from = cache.get_or_set(f'{order_id}_coord_from',
#                                   client.coordinates(address_from), 130)
#     coord_to = cache.get_or_set(f'{order_id}_coord_to',
#                                 client.coordinates(address_to), 130)
#     dist = cache.get_or_set(f'{order_id}_distance',
#                      round(distance.distance(coord_from, coord_to).km, 2), 130)
#     return dist

def get_restaurants_info(order, restaurant_item_cls):
    products_ids = order.products.all().values_list('product_id', flat=True)
    restaurants = [
        [restaurant for restaurant in restaurant_item_cls.objects.filter(
            product_id=product_id, availability=True).values_list(
            'restaurant__name', 'restaurant__address')
         ] for product_id in products_ids
    ]
    complete_data = {}
    if restaurants:
        for rest, address in reduce(set.intersection, map(set, restaurants)):
            try:
                complete_data[rest] = get_distance(address, order.address, order.id)
            except (InvalidKey, NothingFound):
                complete_data[rest] = 0

    return OrderedDict(sorted(complete_data.items(), key=lambda k: k[1]))
    return []
