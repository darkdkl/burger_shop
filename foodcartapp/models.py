from functools import reduce
from operator import and_

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, Q
from django.db.utils import IntegrityError
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50,
                                     blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 verbose_name='категория',
                                 related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False,
                                         db_index=True)
    ingredients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE,
                                   related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class OrderItem(models.Model):
    product = models.ForeignKey(Product, related_name="ordered", null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    quantity = models.IntegerField(verbose_name="Количество",
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    price = models.FloatField(verbose_name="Цена", null=True)

    order = models.ForeignKey("Order", related_name="products",
                              on_delete=models.CASCADE,
                              verbose_name="Заказ")
    total_cost = models.FloatField(verbose_name="Сумма", default=0)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        if self.quantity:
            self.total_cost = self.quantity * self.price
        super().save(*args, **kwargs)
        self.order.calculate_total_cost

    def __str__(self):
        return self.product.name


class Order(models.Model):
    ORDER_STATUSES = [
        ('not', 'Не обработан'),
        ('in', 'В обработке'),
        ('com', 'Выполнен'),
        ('rej', 'Отменен'),
    ]
    PAYMENT_OPTION = [
        ('cashless', 'Безналичный'),
        ('cash', 'Наличный')
    ]
    firstname = models.CharField(verbose_name="Имя", max_length=150)
    lastname = models.CharField(verbose_name="Фамилия", max_length=150)
    phonenumber = PhoneNumberField(verbose_name='Телефон')
    address = models.CharField(verbose_name="Адрес доставки",
                               max_length=250)
    status = models.CharField(max_length=3, choices=ORDER_STATUSES, default='not')
    total_cost = models.FloatField("Сумма заказа", default=0)
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    called = models.DateTimeField(blank=True, null=True)
    delivered = models.DateTimeField(blank=True, null=True)
    type_payment = models.CharField(max_length=8, choices=PAYMENT_OPTION, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL,
                                   blank=True, null=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    @property
    def calculate_total_cost(self):
        self.total_cost = self.products.aggregate(cost=Sum("total_cost")
                                                  ).get('cost')
        self.save()

    @property
    def get_restaurants(self):
        products_ids = self.products.all().values_list('product_id', flat=True)
        restaurants = [
             [restaurant for restaurant in RestaurantMenuItem.objects.filter(
                       product_id=product_id, availability=True).values_list(
                       'restaurant__name', flat=True)
             ] for product_id in products_ids
                      ]
        if restaurants:
            return reduce(set.intersection, map(set, restaurants))
        return []

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
