from django.contrib import admin
from .models import Category, Dish, Contact,Booking

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']

# Dish Admin
class DishAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    list_filter = ['category', 'is_available']
    search_fields = ['name']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
from django.contrib import admin
from .models import Category, Order, Dish, OrderItem, Profile

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)
admin.site.register(Contact)
admin.site.register(Booking)