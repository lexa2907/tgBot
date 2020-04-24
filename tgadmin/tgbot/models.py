from django.db import models


class Users(models.Model):
    name = models.PositiveIntegerField('id_пользователя', unique=True)
    nickname = models.CharField('има пользователя', max_length=100)
    mobile = models.CharField('Телефон', max_length=11, blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)
    delivery = models.CharField('Тип доставки', max_length=15, default='🚗 Привезти')
    time_delivery = models.CharField('Время доставки', max_length=20, default='Как можно скорее')
    status = models.CharField(max_length=1, default='1')
    basket_sum = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '{}'.format(self.nickname)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'


class Orders(models.Model):
    data = models.DateTimeField('Дата и время заказа', auto_now_add=True)
    amount_to_pay = models.PositiveIntegerField('Сумма в ₽')
    type_delivery = models.CharField('Тип доставки', max_length=15)
    address_delivery = models.CharField('Адрес доставки', max_length=100, null=True)
    time_delivery = models.CharField('Время доставки', max_length=50)
    food = models.TextField('Позиции')
    users = models.ForeignKey(Users, models.CASCADE, verbose_name='Заказ пользователя')

    def __str__(self):
        return '{}'.format(self.users)

    class Meta:
        verbose_name = 'Заказы '
        verbose_name_plural = 'Заказы пользователей'


class Basket(models.Model):
    product_id = models.CharField(max_length=250, blank=True, null=True, db_index=True)
    count = models.IntegerField('Количество', blank=True, null=True)
    baskUser = models.ForeignKey(Users, models.CASCADE, verbose_name='Продукт пользователя')
    name_product = models.CharField('Наименование товара', max_length=250)
    photo = models.URLField('URL фото продукта')
    price = models.DecimalField('Цена', max_digits=8, decimal_places=0, default=0)

    def __str__(self):
        return self.name_product

    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователей'


class CategoryOne(models.Model):
    name = models.CharField('Название кухни', max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Первая категория'
        verbose_name_plural = 'Первая категория'


class CategoryTwo(models.Model):
    name = models.CharField('Наименование раздела', max_length=250)
    category_two = models.ForeignKey(CategoryOne, models.CASCADE, verbose_name='Категория-1', null=True, blank=True)

    class Meta:
        verbose_name = 'Вторая категория'
        verbose_name_plural = 'Вторая категория'

    def __str__(self):
        return self.name


class AllMenu(models.Model):
    name = models.CharField('Название товара', max_length=250)
    structure = models.CharField('Состав', max_length=250,)
    photo = models.URLField('URL фото продукта', blank=True, null=True)
    weight = models.DecimalField('Вес в гр.', max_digits=7, decimal_places=0, blank=True, null=True)
    volume = models.PositiveSmallIntegerField('Количество-шт(Пицца-см)', null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=0, default=0)
    category_two = models.ForeignKey(CategoryTwo, models.CASCADE, verbose_name='Категория-2')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Все товары'
