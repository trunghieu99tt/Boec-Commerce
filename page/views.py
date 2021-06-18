import json
import pandas as pd
from apyori import apriori

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from page.forms import ContactForm, SearchForm
from page.models import ContactMessage, Shop
from product.models import Category, Product, Images, Comment, Variants, WishList
from order.models import OrderProduct, Order


def index(request):

    products_latest = Product.objects.filter(status="True").order_by(
        '-id')[:4]  # last 4 products

    products_slider = Product.objects.filter(status="True").order_by('id')[
        :4]  # first 4 products

    products_picked = Product.objects.filter(status="True").order_by(
        '?')[:4]  # Random selected 4 products

    # page = "home"
    categories = Category.objects.all()

    # Get site info
    siteInfo = Shop.objects.all().first()

    print(siteInfo)

    context = {
        # 'page': page,
        'products_slider': products_slider,
        'products_latest': products_latest,
        'products_picked': products_picked,
        'categories': categories,
        'siteInfo': siteInfo
    }
    return render(request, 'pages/index.html', context)


def aboutus(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'pages/about.html', context)


def contactus(request):
    if request.method == 'POST':  # check post
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage()  # create relation with model
            data.name = form.cleaned_data['name']  # get form input data
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  # save data to table
            messages.success(
                request, "Your message has ben sent. Thank you for your message.")
            return HttpResponseRedirect('/contact')

    categories = Category.objects.all()
    form = ContactForm
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'pages/contactus.html', context)


def category_products(request, id):

    # Lấy ra min Price, maxPrice
    if request.GET.get('minPrice'):
        minPrice = request.GET.get('minPrice')
    else:
        minPrice = 0
    if request.GET.get('maxPrice'):
        maxPrice = request.GET.get('maxPrice')
    else:
        maxPrice = 999
    if request.GET.get('sortBy'):
        sortBy = request.GET.get('sortBy')
    else:
        sortBy = 'price'
    categories = Category.objects.all()
    catdata = Category.objects.get(pk=id)

    # Lọc theo khoảng giá
    products = Product.objects.filter(
        category_id=id, price__range=(minPrice, maxPrice)).order_by(sortBy)

    # Get site info
    siteInfo = Shop.objects.all().first()

    print(siteInfo)

    context = {'products': products,
               'categories': categories,
               'catdata': catdata,
               'minPrice': minPrice,
               'maxPrice': maxPrice,
               'siteInfo': siteInfo
               }
    return render(request, 'pages/category_products.html', context)


def search(request):
    if request.method == 'POST':  # check post
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']  # get form input data
            products = Product.objects.filter(title__icontains=query)

            category = Category.objects.all()
            # Get site info
            siteInfo = Shop.objects.all().first()
            context = {'products': products, 'query': query,
                       'categories': category,
                       'siteInfo': siteInfo
                       }
            return render(request, 'pages/search_products.html', context)

    return HttpResponseRedirect('/')


def product_detail(request, id, slug):
    query = request.GET.get('q')
    category = Category.objects.all()
    product = Product.objects.get(pk=id)

    images = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id, status='True')
    suggests = suggest_pro(id)

    # Get site info
    siteInfo = Shop.objects.all().first()
    # print(suggests)
    context = {'product': product, 'category': category,
               'images': images, 'comments': comments,
               'suggests': suggests,
               'categories': category,
               'siteInfo': siteInfo
               }
    if product.variant != "None":  # Product have variants
        if request.method == 'POST':  # if we select color
            variant_id = request.POST.get('variantid')
            # selected product by click color radio
            variant = Variants.objects.get(id=variant_id)
            colors = Variants.objects.filter(
                product_id=id, size_id=variant.size_id)
            sizes = Variants.objects.raw(
                'SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title+' Size:' + \
                str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(
                product_id=id, size_id=variants[0].size_id)
            sizes = Variants.objects.raw(
                'SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            variant = Variants.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors,
                        'variant': variant, 'query': query,
                        'categories': category
                        })
    return render(request, 'product/product_detail.html', context)


def ajaxcolor(request):
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string(
            'components/color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)


def suggest_pro(id):
    orders = Order.objects.all()
    list_orders = []
    for order in orders:
        orderproducts = OrderProduct.objects.filter(order_id=order.id)
        if (len(orderproducts) > 1):
            list_products = []
            for orderproduct in orderproducts:
                list_products.append(str(orderproduct.product_id))
            list_orders.append(list_products)
    df = pd.DataFrame(list_orders)
    records = []
    for i in range(df.shape[0]):
        records.append([str(df.values[i, j])
                       for j in range(df.shape[1])])

    association_rules = apriori(
        records, min_support=0.3, min_confidence=0.5, min_lift=1.2)
    association_results = list(association_rules)
    list_results = []
    for i in range(len(association_results)):
        for j in range(len(association_results[i][2])):
            item_base = list(association_results[i][2][j][0])
            item_add = list(association_results[i][2][j][1])
            if len(item_base) == 1:
                if item_base[0] == str(id):
                    for item in item_add:
                        if item != 'None':
                            pro = Product.objects.get(pk=int(item))
                            if pro.status == "True":
                                if pro not in list_results:
                                    list_results.append(pro)

    return list_results
