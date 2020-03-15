from django.contrib import admin
from .models import *


@admin.register(Arrr)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Orders)
class UsersAdmin(admin.ModelAdmin):
    list_display =['data', 'amount_to_pay', 'type_delivery', 'address_delivery', 'food', 'users', 'time_delivery']


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['name','nickname','mobile','address','delivery','time_delivery']
    search_fields = ('nickname',)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name_product', 'baskUser', 'count', 'id','price']


@admin.register(Meni)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'structure', 'photo', 'price', 'weight', 'lol']
    search_fields = ('lol__name', 'name',)
    ordering = ('lol',)
    list_filter = ('lol',)


@admin.register(Category1)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'lol']
    search_fields = ('name','lol__name',)
    ordering = ('lol',)
    list_filter = ('lol',)







# Register your models here.
