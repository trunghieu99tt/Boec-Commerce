from page.models import ContactMessage, Shop
from django.contrib import admin


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'update_at', 'status']
    readonly_fields = ('name', 'subject', 'email', 'message', 'ip')
    list_filter = ['status']


class ShopAdmin(admin.ModelAdmin):
    list_display: ['name', 'address']


admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Shop, ShopAdmin)
