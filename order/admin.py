from django.contrib import admin
from order.models import ShopCart, Order, OrderProduct
from product.models import Product


class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'quantity', 'price', 'amount']
    list_filter = ['user', ]


class OrderProductline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'price',
                       'quantity', 'amount', 'status')
    can_delete = False
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',
                    'phone', 'city', 'total', 'status']
    list_filter = ['status']
    readonly_fields = ('user', 'address', 'city', 'phone',
                       'first_name', 'ip', 'last_name', 'phone', 'city', 'total')
    can_delete = False
    inlines = [OrderProductline]
    actions = ['make_new', 'make_accepted',
               'make_preparing', 'make_onShipping', 'make_completed', 'make_cancle', ]

    @admin.action(description='Cancel order')
    def make_cancle(self, request, queryset):
        for order in queryset:
            if order.status != 'Canceled':
                orderproducts = OrderProduct.objects.filter(order_id=order.id)
                for orderproduct in orderproducts:
                    product = Product.objects.get(pk=orderproduct.product_id)
                    product.amount += orderproduct.quantity
                    orderproduct.status = 'Canceled'
                    orderproduct.save()
                    product.save()
                order.status = 'Canceled'
                order.save()

    @admin.action(description='New order')
    def make_new(self, request, queryset):
        for order in queryset:
            if order.status != 'New':
                if order.status == 'Canceled':
                    orderproducts = OrderProduct.objects.filter(
                        order_id=order.id)
                    for orderproduct in orderproducts:
                        product = Product.objects.get(
                            pk=orderproduct.product_id)
                        product.amount -= orderproduct.quantity
                        orderproduct.status = 'New'
                        orderproduct.save()
                        product.save()
                order.status = 'New'
                order.save()

    @admin.action(description='Accepted order')
    def make_accepted(self, request, queryset):
        for order in queryset:
            if order.status != 'Accepted':
                if order.status == 'Canceled':
                    orderproducts = OrderProduct.objects.filter(
                        order_id=order.id)
                    for orderproduct in orderproducts:
                        product = Product.objects.get(
                            pk=orderproduct.product_id)
                        product.amount -= orderproduct.quantity
                        product.save()
                        orderproduct.status = 'New'
                        orderproduct.save()
                order.status = 'Accepted'
                order.save()

    @admin.action(description='Preparing order')
    def make_preparing(self, request, queryset):
        for order in queryset:
            if order.status != 'Preparing':
                if order.status == 'Canceled':
                    orderproducts = OrderProduct.objects.filter(
                        order_id=order.id)
                    for orderproduct in orderproducts:
                        product = Product.objects.get(
                            pk=orderproduct.product_id)
                        product.amount -= orderproduct.quantity
                        product.save()
                        orderproduct.status = 'New'
                        orderproduct.save()
                order.status = 'Preparing'
                order.save()

    @admin.action(description='OnShipping order')
    def make_onShipping(self, request, queryset):
        for order in queryset:
            if order.status != 'OnShipping':
                if order.status == 'Canceled':
                    orderproducts = OrderProduct.objects.filter(
                        order_id=order.id)
                    for orderproduct in orderproducts:
                        product = Product.objects.get(
                            pk=orderproduct.product_id)
                        product.amount -= orderproduct.quantity
                        product.save()
                        orderproduct.status = 'New'
                        orderproduct.save()
                order.status = 'OnShipping'
                order.save()

    @admin.action(description='Completed order')
    def make_completed(self, request, queryset):
        for order in queryset:
            if order.status != 'Completed':
                if order.status == 'Canceled':
                    orderproducts = OrderProduct.objects.filter(
                        order_id=order.id)
                    for orderproduct in orderproducts:
                        product = Product.objects.get(
                            pk=orderproduct.product_id)
                        product.amount -= orderproduct.quantity
                        product.save()
                        orderproduct.status = 'New'
                        orderproduct.save()
                order.status = 'Completed'
                order.save()


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'price',
                    'quantity', 'amount', 'status', ]
    list_filter = ['user']
    actions = ['make_new', 'make_accepted', 'make_cancle', ]

    @admin.action(description='Cancel item')
    def make_cancle(self, request, queryset):
        for orderproduct in queryset:
            if orderproduct.status != 'Canceled':
                product = Product.objects.get(pk=orderproduct.product_id)
                product.amount += orderproduct.quantity
                product.save()
                orderproduct.status = 'Canceled'
                orderproduct.save()
        orders = Order.objects.all()
        for order in orders:
            orderproducts = OrderProduct.objects.filter(order_id=order.id)
            flag = False
            for orderproduct in orderproducts:
                print(orderproduct.__dict__)
                if orderproduct.status != 'Canceled':
                    flag = True
                    break
            if flag is False:
                order.status = 'Canceled'
                order.save()

    @admin.action(description='New item')
    def make_new(self, request, queryset):
        for orderproduct in queryset:
            if orderproduct.status != 'New':
                if orderproduct.status == 'Canceled':
                    product = Product.objects.get(pk=orderproduct.product_id)
                    product.amount -= orderproduct.quantity
                    product.save()
                orderproduct.status = 'New'
                orderproduct.save()
        orders = Order.objects.all()
        for order in orders:
            orderproducts = OrderProduct.objects.filter(order_id=order.id)
            flag = False
            for orderproduct in orderproducts:
                print(orderproduct.__dict__)
                if orderproduct.status != 'Canceled':
                    flag = True
                    break
            if flag is False:
                order.status = 'Canceled'
            else:
                if order.status == 'Canceled':
                    order.status = 'New'
            order.save()

    @admin.action(description='Accepted item')
    def make_accepted(self, request, queryset):
        for orderproduct in queryset:
            if orderproduct.status != 'Accepted':
                if orderproduct.status == 'Canceled':
                    product = Product.objects.get(pk=orderproduct.product_id)
                    product.amount -= orderproduct.quantity
                    product.save()
                orderproduct.status = 'Accepted'
                orderproduct.save()
        orders = Order.objects.all()
        for order in orders:
            orderproducts = OrderProduct.objects.filter(order_id=order.id)
            flag = False
            for orderproduct in orderproducts:
                print(orderproduct.__dict__)
                if orderproduct.status != 'Canceled':
                    flag = True
                    break
            if flag is False:
                order.status = 'Canceled'
            else:
                if order.status == 'Canceled':
                    order.status = 'New'
            order.save()


admin.site.register(ShopCart, ShopCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
