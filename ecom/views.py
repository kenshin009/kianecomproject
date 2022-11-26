import stripe
import json
from django.db.models import Q
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.shortcuts import render, redirect
from .models import *
from .forms import SignupForm
from django.views import View
from django.http import JsonResponse

# Create your views here.

def signup(request):

    if request.user.is_authenticated:
        return redirect('ecom:myaccount')
    else:
        pass

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('/')
    else:
        form = SignupForm()

    return render(request,'signup.html',{
        'form': form
    })

def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        
        if user is not None:
            login(request,user)
            if 'next' in request.GET:
                next_url = request.GET.get('next')
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            form = AuthenticationForm(request.POST)
            return render(request,'login.html',{'form':form,'message':'Invalid creditial'})
    else:
        form = AuthenticationForm()

    return render(request,'login.html',{'form': form})

def logout_view(request):

    logout(request)
    return redirect('/')

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()


    active_category = request.GET.get('category','')
    if active_category:
        products = products.filter(category__slug=active_category)

    query = request.GET.get('query','')
    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(request,'home.html',{
        'categories': categories,
        'products': products,
        'active_category': active_category
    })

def about(request):

    return render(request,'about.html')


def product_detail(request,slug):

    product = Product.objects.get(slug=slug)
    return render(request, 'product_detail.html',{
        'product': product
    })

def add_to_cart(request,slug):

    product_obj = Product.objects.get(slug=slug)
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
        if product_in_cart.exists():
            cartproduct = product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.price = product_obj.price
            cartproduct.subtotal += product_obj.price
            cartproduct.save()
            cart_obj.total += product_obj.price
            cart_obj.save()
        else:
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, price=product_obj.price,
                        quantity=1,subtotal=product_obj.price,)
            cart_obj.total += product_obj.price
            cart_obj.save()
    else:
        cart_obj = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_obj.id
        cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, price=product_obj.price,
                        quantity=1,subtotal=product_obj.price,)
        cart_obj.total += product_obj.price
        cart_obj.save()

    return redirect('ecom:home')

def mycart(request):

    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        cp = cart_obj.cartproduct_set.all
    else:
        cart_obj = None
        return render(request,'mycart.html',{'cart': cart_obj})

    return render(request,'mycart.html',{
        'cart': cart_obj,
        'cartproduct': cp
        })

def manage_cart(request,**kwargs):
    cp_id = kwargs['cp_id']
    cartproduct = CartProduct.objects.get(id=cp_id)
    cart = cartproduct.cart
    action = request.GET.get('action')
    if action == 'inc':
        cartproduct.quantity += 1
        cartproduct.subtotal += cartproduct.price
        cartproduct.save()
        cart.total += cartproduct.price
        cart.save()
    elif action == 'dcr':
        
            cartproduct.quantity -= 1
            cartproduct.subtotal -= cartproduct.price
            cartproduct.save()
            cart.total -= cartproduct.price
            cart.save()

            if cartproduct.quantity == 0:
                cartproduct.delete()
        
    elif action == 'rmv':
        cart.total -= cartproduct.subtotal
        cart.save()
        cartproduct.delete()

    else:
        pass
    return redirect('ecom:mycart')


def checkout(request):

    if request.user.is_authenticated and request.user:
        pass
    else:
        return redirect('/login/?next=/checkout/')

    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        cartproduct = cart_obj.cartproduct_set.all()
            
    else:
        return redirect('/')

    return render(request,'checkout.html',{
        'cart': cart_obj,
        'cartproduct': cartproduct,
        'pub_key': settings.STRIPE_PUBLIC_KEY
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

def make_order(request,pk):
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        cart_obj = Cart.objects.get(pk=pk)
        cartproduct = cart_obj.cartproduct_set.all()
        print(cartproduct)
        total_price = 0
        items = []

        for item in cartproduct:
            product = item.product
            total_price += item.price * item.quantity
            obj ={
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': product.price_id,
                    'quantity': item.quantity,
                }
            items.append(obj)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items= items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )

        if request.method == 'POST':    
            customer = request.POST.get('customer')
            address = request.POST.get('address')        
            phone = request.POST.get('phone')
            email = request.POST.get('email')

            order = Order.objects.create (cart=cart_obj, ordered_by=customer,shipping_address=address,phone=phone,email=email,
                                        subtotal=cart_obj.total,discount=0,total=cart_obj.total,order_status='Order received')
                    
            del request.session['cart_id']
            return redirect(checkout_session.url, code=303)

        return redirect(checkout_session.url, code=303)

def success(request):

    return render(request, 'success.html')

def cancel(request):

    return render(request, 'cancel.html')

def myaccount(request):

    return render(request,'myaccount.html')