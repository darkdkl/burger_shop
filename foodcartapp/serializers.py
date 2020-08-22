from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.Serializer):
    product = serializers.SlugField()
    quantity = serializers.IntegerField()

    def validate_product(self, data):
        if not Product.objects.filter(id=data).exists():
            raise serializers.ValidationError(
                'product c таким ID не существует')
        return data


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = PhoneNumberField()
    address = serializers.CharField()
    products = OrderItemSerializer(many=True)

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products:
            OrderItem.objects.create(product_id=product['product'],
                                     quantity=product['quantity'],
                                     order=order)
        return order

    def validate_firstname(self, data):
        if data.isdigit():
            raise serializers.ValidationError(
                'firstname может быть только строкой')
        return data

    def validate_lastname(self, data):
        if data.isdigit():
            raise serializers.ValidationError(
                'lastname может быть только строкой')
        return data

    def validate_products(self, data):
        if not data:
            raise serializers.ValidationError(
                'products не может быть пустым')
        return data

    def validate_address(self, data):
        address = data.replace(" ", "")
        if len(address) < 20 or address.isnumeric():
            raise serializers.ValidationError(
                'address не корректен')

        return data
