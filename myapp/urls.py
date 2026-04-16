from django.urls import path , include

from headquaters import settings
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name='home'),
    # path('login/', views.login_view, name='login'), 
    # path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('booking/', views.booking, name='booking'),
    path('checkout/', views.checkout, name='checkout'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('team/', views.team, name='team'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:dish_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:dish_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart-ajax/<int:dish_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('update-cart/<int:dish_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('get-distance/', views.calculate_distance_ajax, name='get_distance'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)