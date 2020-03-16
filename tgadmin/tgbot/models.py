from django.db import models


class Users(models.Model):
    name = models.PositiveIntegerField(unique=True, blank=True, null=True) # заменить на pozitivInteger переименовать id_name
    nickname = models.CharField('има пользователя',max_length=100, blank=True, null=True) # на charfield поменять
    mobile = models.CharField(max_length=11,blank=True, null=True) # на сharfield поменять
    address = models.TextField(blank=True, null=True)
    delivery = models.CharField('тип доставки', max_length=15, default='🚗 Привезти')
    time_delivery = models.CharField('время доставки',max_length=20,default='Как можно скорее')

    def __str__(self):
        return '{}'.format(self.nickname)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'


class Orders(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    amount_to_pay = models.PositiveIntegerField()
    type_delivery = models.CharField('тип доставки', max_length=15)
    address_delivery = models.CharField(max_length=100)  # null = True не забыть поставить
    time_delivery = models.CharField(max_length=50)
    food = models.TextField()
    users = models.ForeignKey(Users, models.CASCADE, verbose_name='продукт юзера')


class Basket(models.Model):
    product_id = models.CharField(max_length=250, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    baskUser = models.ForeignKey(Users, models.CASCADE, verbose_name='продукт юзера', null=True, blank=True)
    name_product = models.CharField(max_length=250, blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    weight = models.DecimalField('вес в гр.', max_digits=7, decimal_places=0, blank=True, null=True)
    price = models.DecimalField('цена', max_digits=8, decimal_places=0, default=0, blank=True, null=True)

    def __str__(self):
        return self.product_id
    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователей'

class Arrr(models.Model):
    name = models.CharField(max_length=250)
    unic = models.CharField(max_length=250, unique=True, null=True, blank=True, db_index=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Первая Категория'
        verbose_name_plural = 'Первая категория'

class Category1(models.Model):
    name = models.CharField(max_length=250)
    lol = models.ForeignKey(Arrr, models.CASCADE, verbose_name='категория1', null=True, blank=True)
    unicс = models.CharField(max_length=250, unique=True, null=True, blank=True, db_index=True)# Тут буква c русская

    class Meta:
        verbose_name = 'Вторая Категория'
        verbose_name_plural = 'Вторая категория'
    def __str__(self):
        return self.name


class Meni(models.Model):
    name = models.CharField(max_length=250)
    unic = models.CharField(max_length=250, null=True, blank=True, db_index=True)
    structure = models.CharField(max_length=250, blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    weight = models.DecimalField('вес в гр.', max_digits=7, decimal_places=0, blank=True, null=True)
    price = models.DecimalField('цена', max_digits=8, decimal_places=0, default=0, blank=True, null=True)
    lol = models.ForeignKey(Category1, models.CASCADE, verbose_name='категория2', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Все товары'

