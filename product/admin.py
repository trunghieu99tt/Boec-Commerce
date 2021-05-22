import admin_thumbnails
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from product.models import Category, Product, Images, Comment, Color, Size, Variants


class CategoryAdmin(ModelAdmin):
    list_display = ('title', 'related_products_count')
    prepopulated_fields = {'slug': ('title',)}

    def related_products_count(self, instance):
        product_qty = Product.objects.filter(category=instance).count()
        return product_qty
    related_products_count.short_description = 'Related products (for this specific category)'


@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1


class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True


@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image', 'title', 'image_thumbnail']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'image_tag']
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline, ProductVariantsInline]
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ['subject', 'comment', 'status', 'create_at']
    list_filter = ['status']
    readonly_fields = ('subject', 'comment', 'ip',
                       'user', 'product', 'rate', 'id')


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_tag']


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'color',
                    'size', 'price', 'quantity', 'image_tag']


# class ProductLangugaeAdmin(admin.ModelAdmin):
#     list_display = ['title', 'lang', 'slug']
#     prepopulated_fields = {'slug': ('title',)}
#     list_filter = ['lang']


# class CategoryLangugaeAdmin(admin.ModelAdmin):
#     list_display = ['title', 'lang', 'slug']
#     prepopulated_fields = {'slug': ('title',)}
#     list_filter = ['lang']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Variants, VariantsAdmin)
