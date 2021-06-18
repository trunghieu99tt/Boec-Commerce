from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import Group, User


from django.utils import translation

from order.models import Order, OrderProduct
from product.models import Category, Comment, WishList, WishlistItem, Product
from user.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from user.models import UserProfile


@login_required(login_url='/login')  # Check login
def index(request):
    categories = Category.objects.all()
    current_user = request.user  # Access User Session information
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {
        'categories': categories,
        'profile': profile}
    return render(request, 'user/user_profile.html', context)


def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = request.user
            userprofile = UserProfile.objects.get(user_id=current_user.id)
            request.session['userimage'] = userprofile.image.url
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group == 'warehouse_staff':
                return HttpResponseRedirect('/warehouse_staff/')
            elif group == 'sale_staff':
                return HttpResponseRedirect('/sale_staff/')
            elif group == 'business_staff':
                return HttpResponseRedirect('/business_staff/')

            return HttpResponseRedirect('/')
        else:
            messages.warning(
                request, "Login Error !! Username or Password is incorrect")
            return HttpResponseRedirect('/login')

    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'user/login_form.html', context)


# @login_required(login_url='/login')
# def business_staff_view(request):
#     if request.user.groups.exists():
#         group = request.user.groups.all()[0].name

#     if group == 'business_staff':
#         return render(request, 'user/business_staff.html')
#     else:
#         return HttpResponse('You are not authorized to view this page')


# @login_required(login_url='/login')
# def sale_staff_view(request):
#     if request.user.groups.exists():
#         group = request.user.groups.all()[0].name

#     if group == 'sale_staff':
#         orders = Order.objects.all()
#         users = UserProfile.objects.all()
#         customers = []
#         for u in users:
#             if u.user.groups.exists():
#                 if u.user.groups.all()[0].name == 'customer':
#                     customers.append(u)

#         total_customers = len(customers)
#         for cu in customers:
#             print(cu.user.first_name)
#         total_orders = orders.count()
#         delivered = orders.filter(status='Completed').count()
#         pending = orders.filter(status='Preaparing').count()

#         context = {'orders': orders, 'customers': customers,
#                    'total_orders': total_orders, 'delivered': delivered,
#                    'pending': pending}

#         return render(request, 'accounts/dashboard.html', context)
#         # return render(request, 'user/business_staff.html')
#     else:
#         return HttpResponse('You are not authorized to view this page')


# @login_required(login_url='/login')
# def warehouse_staff_view(request):
#     if request.user.groups.exists():
#         group = request.user.groups.all()[0].name

#     if group == 'warehouse_staff':

#         return render(request, 'user/warehouse_staff.html')
#     else:
#         return HttpResponse('You are not authorized to view this page')


def logout_func(request):
    logout(request)
    if 'userimage' in request.session:
        del request.session['userimage']
    return HttpResponseRedirect('/')


def signup_form(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # completed sign up
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            group = Group.objects.get(name='customer')
            login(request, user)
            # Create data in profile table for user
            current_user = request.user
            current_user.groups.add(group)
            data = UserProfile()
            data.user_id = current_user.id
            data.image = "images/users/user.png"
            data.save()
            messages.success(request, 'Your account has been created!')
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('/signup')

    form = SignUpForm()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'user/signup_form.html', context)


@login_required(login_url='/login')  # Check login
def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            request.session['userimage'] = request.user.userprofile.image.url
            messages.success(request, 'Your account has been updated!')
            return HttpResponseRedirect('/user')
    else:
        categories = Category.objects.all()
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
        context = {
            'categories': categories,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'user/user_update.html', context)


@login_required(login_url='/login')  # Check login
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(
                request, 'Please correct the error below.<br>' + str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'user/user_password.html', {'form': form})


@login_required(login_url='/login')  # Check login
def user_orders(request):
    #category = Category.objects.all()
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id)
    context = {  # 'category': category,
        'orders': orders,
    }
    return render(request, 'user/user_orders.html', context)


@login_required(login_url='/login')  # Check login
def user_orderdetail(request, id):
    #category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    orderitems = OrderProduct.objects.filter(order_id=id)
    context = {
        # 'category': category,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'user/user_order_detail.html', context)


@login_required(login_url='/login')  # Check login
def user_order_product(request):
    #category = Category.objects.all()
    current_user = request.user
    order_product = OrderProduct.objects.filter(
        user_id=current_user.id).order_by('-id')
    context = {  # 'category': category,
        'order_product': order_product,
    }
    return render(request, 'user/user_order_products.html', context)


@login_required(login_url='/login')  # Check login
def user_order_product_detail(request, id, oid):
    #category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    orderitems = OrderProduct.objects.filter(id=id, user_id=current_user.id)
    context = {
        # 'category': category,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'user/user_order_detail.html', context)


def user_comments(request):
    category = Category.objects.all()
    current_user = request.user
    comments = Comment.objects.filter(user_id=current_user.id)
    context = {
        'categories': category,
        'comments': comments,
    }
    return render(request, 'user/user_comments.html', context)


@login_required(login_url='/login')  # Check login
def user_deletecomment(request, id):
    current_user = request.user
    Comment.objects.filter(id=id, user_id=current_user.id).delete()
    messages.success(request, 'Comment deleted..')
    return HttpResponseRedirect('/user/comments')


@login_required(login_url='/login')
def add_product(request):
    if request.methods == "GET":
        return HttpResponseRedirect('/signup')
    if request.methods == "POST":
        pass


@login_required(login_url='/login')  # Check login
def user_wishlist(request):
    currentUser = request.user
    if not WishList.objects.filter(user_id=currentUser.id).exists():
        wishlist = WishList()
        wishlist.user_id = currentUser.id
        wishlist.title = "Wishlist"
        wishlist.description = "Description"
        wishlist.save()
    else:
        wishlist = WishList.objects.filter(user_id=currentUser.id).first()
    print('wishlist: {}'.format(wishlist.id))
    wishlistItems = WishlistItem.objects.filter(wishlist_id=wishlist.id)
    products = []
    for rs in wishlistItems:
        product = Product.objects.get(pk=rs.product_id)
        products.append(product)
    context = {
        'products': products
    }
    return render(request, 'user/wishlist.html', context)


@login_required(login_url='/login')  # Check login
def addToWishlist(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    currentUser = request.user
    if not WishList.objects.filter(user_id=currentUser.id).exists():
        wishlist = WishList()
        wishlist.user_id = currentUser.id
        wishlist.title = "Wishlist"
        wishlist.description = "Description"
        wishlist.save()
    else:
        wishlist = WishList.objects.filter(user_id=currentUser.id).first()
    if not WishlistItem.objects.filter(wishlist_id=wishlist.id):
        newWishlistItem = WishlistItem()
        newWishlistItem.wishlist_id = wishlist.id
        newWishlistItem.product_id = id
        newWishlistItem.save()
        messages.success(request, "Product added to wishlist ")
    else:
        messages.success(request, "Product already in wishlist ")
    return HttpResponseRedirect(url)


@login_required(login_url='/login')  # Check login
def removeFromWishlist(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    currentUser = request.user
    wishlist = WishList.objects.filter(user_id=currentUser.id).first()
    if not WishlistItem.objects.filter(wishlist_id=wishlist.id):
        messages.error(request, "Product is not in wishlist")
    else:
        WishlistItem.objects.filter(
            wishlist_id=wishlist.id, product_id=id).delete()
        messages.success(request, "Delete product succesfully!")
    return HttpResponseRedirect(url)
