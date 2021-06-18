from django.db import models


class ContactMessage(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Read', 'Read'),
        ('Closed', 'Closed'),
    )
    name = models.CharField(blank=True, max_length=20)
    email = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=50)
    message = models.TextField(blank=True, max_length=255)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    note = models.CharField(blank=True, max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(blank=True, max_length=20)
    address = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return self.name

    def save(self):
        count = Shop.objects.all().count()
        save_permission = Shop.has_add_permission(self)
        if count < 1:
            super(Shop, self).save()
        elif save_permission:
            super(Shop, self).save()

    def has_add_permission(self):
        return Shop.objects.filter(id=self.id).exists()
