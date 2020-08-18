from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
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
    product=models.ForeignKey(Product,related_name="ordered",null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    quantity = models.IntegerField(verbose_name="Количество",
                                   validators=[MinValueValidator(0)])

    order = models.ForeignKey("Order", related_name="items",
                              on_delete=models.CASCADE,
                              verbose_name="Заказ")

    def __str__(self):
        return self.product.name


class Order(models.Model):
    customer_first_name = models.CharField(verbose_name="Имя",max_length=150)
    customer_last_name = models.CharField(verbose_name="Фамилия",max_length=150)
    customer_phone = PhoneNumberField(verbose_name='Телефон')
    customer_address = models.CharField(verbose_name="Адрес доставки",
                                       max_length=250)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name} " \
               f"{self.customer_address}"
