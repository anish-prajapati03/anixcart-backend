from django.contrib import admin
from django.utils.html import format_html
from .models import Product, CartItem, Order, OrderItem

admin.site.site_header = "AnixCart Admin"
admin.site.site_title = "AnixCart"
admin.site.index_title = "Welcome to AnixCart Admin Panel"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('preview_image', 'name', 'category', 'price_inr', 'stock', 'stock_status', 'created_at')
    list_display_links = ('preview_image', 'name')
    list_editable = ('stock', 'category')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'preview_image_large')

    fieldsets = (
        ('Product Info', {
            'fields': ('name', 'description', 'price', 'category')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Image', {
            'fields': ('image', 'preview_image_large')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def price_inr(self, obj):
        return f"₹{obj.price:,.2f}"
    price_inr.short_description = 'Price'
    price_inr.admin_order_field = 'price'

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:red;font-weight:bold;">Out of Stock</span>')
        elif obj.stock <= 5:
            return format_html('<span style="color:orange;font-weight:bold;">Low ({})</span>', obj.stock)
        return format_html('<span style="color:green;font-weight:bold;">In Stock</span>')
    stock_status.short_description = 'Status'

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:6px;" />', obj.image)
        return '—'
    preview_image.short_description = 'Image'

    def preview_image_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:200px;height:150px;object-fit:cover;border-radius:10px;margin-top:8px;" />', obj.image)
        return '—'
    preview_image_large.short_description = 'Preview'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'qty', 'item_total')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('user', 'product', 'qty')

    def item_total(self, obj):
        return f"₹{obj.product.price * obj.qty:,.2f}"
    item_total.short_description = 'Total'

    def has_add_permission(self, request):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'qty', 'line_total')
    can_delete = False

    def line_total(self, obj):
        return f"₹{obj.price * obj.qty:,.2f}"
    line_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_method', 'total_inr', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'address')
    list_editable = ('status',)
    readonly_fields = ('user', 'address', 'payment_method', 'upi_app', 'upi_id', 'total', 'created_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

    def total_inr(self, obj):
        return f"₹{obj.total:,.2f}"
    total_inr.short_description = 'Total'

    def has_add_permission(self, request):
        return False
