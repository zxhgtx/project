from django.contrib import admin

from .models import Category, Order, OrderItem, Product

admin.site.site_header = "PC STORE"
admin.site.site_title = "PC STORE"
admin.site.index_title = "Управление магазином"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "in_stock")
    list_filter = ("category", "in_stock")
    search_fields = ("name", "description")
    list_editable = ("price", "in_stock")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "price", "quantity", "product")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "phone", "email")
    list_editable = ("status",)
    inlines = [OrderItemInline]
    readonly_fields = ("total", "created_at")
