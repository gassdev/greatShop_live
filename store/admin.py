from django.contrib import admin
from .models import Product, ProductGallery, ReviewRating, Variation
import admin_thumbnails

@admin_thumbnails.thumbnail('photo')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class VariationInline(admin.TabularInline):
    model = Variation
    # readonly_fields = ('product', 'variation_category', 'variation_value')
    extra = 0
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 
            'updated_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name', ) }
    
    inlines = [VariationInline, ProductGalleryInline]



class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 
                    'is_active')
    list_editable = ( 'is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)

