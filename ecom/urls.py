from django.urls import path 
from django.contrib.auth import views
from . import views

app_name = 'ecom'
urlpatterns = [ 
    path('success/',views.success,name='success'),
    path('cancel/',views.cancel,name='cancel'),
    path('make-order/<pk>/',views.make_order,name='make_order'),
    path('myaccount/',views.myaccount,name='myaccount'),
    path('checkout/',views.checkout,name='checkout'),
    path('logout/',views.logout_view,name='logout'),
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup,name='signup'),
    path('manage-cart/<int:cp_id>/',views.manage_cart,name='manage_cart'),
    path('mycart/',views.mycart,name='mycart'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('product-detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

]