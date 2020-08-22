from django.urls import path, include

from .views import (product_list_api, banners_list_api,
                    register_order,foodcart_orders)
from rest_framework import routers
app_name = "foodcartapp"




urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    path('orders/', foodcart_orders),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework'))
]
