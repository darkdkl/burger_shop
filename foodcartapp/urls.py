from django.urls import path, include

from .views import (product_list_api, banners_list_api,
                    register_order,RegisterOrders)

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    path('orders/', RegisterOrders.as_view()),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework'))
]
