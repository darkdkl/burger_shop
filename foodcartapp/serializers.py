from rest_framework import serializers
from .models import Order,OrderItem,Product



class OrderItemSerializer(serializers.Serializer):
    product = serializers.SlugField()
    quantity = serializers.IntegerField()



class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = serializers.CharField()
    address=serializers.CharField()
    products =OrderItemSerializer(many=True)

    def create(self, validated_data):
        products=validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            OrderItem.objects.create(product_id=product['product'],
                                     quantity=product['quantity'],
                                     order=order)
        return order

    def validate_firstname(self, data):

        return data
