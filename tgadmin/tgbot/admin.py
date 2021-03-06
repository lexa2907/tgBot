from django.contrib import admin
from .models import *


@admin.register(CategoryOne)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Orders)
class UsersAdmin(admin.ModelAdmin):
    list_display =['data', 'users', 'amount_to_pay', 'type_delivery', 'address_delivery', 'food', 'time_delivery']


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'mobile', 'address', 'delivery','id','basket_sum']
    search_fields = ('nickname',)
    exclude = ['status','basket_sum']


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name_product', 'baskUser', 'count', 'price']


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['min_sum', 'channel_orders', 'channel_help']
    exclude = ['id_channel_orders', 'id_channel_help','news']


@admin.register(AllMenu)
class AssortmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'structure', 'photo', 'price', 'weight','volume', 'category_one', 'category_two']
    search_fields = ('category_two__name', 'name',)
    ordering = ('category_two', 'category_one',)
    list_filter = ('category_two', 'category_one',)


@admin.register(CategoryTwo)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_two']
    search_fields = ('name', 'category_two__name',)
    ordering = ('category_two',)
    list_filter = ('category_two',)







# Register your models here.
