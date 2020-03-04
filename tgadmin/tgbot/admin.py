from django.contrib import admin
from .models import *




@admin.register(Arrr)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['name','nickname','mobile','address']
    search_fields = ('nickname',)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name_product', 'baskUser', 'count', 'id']


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
