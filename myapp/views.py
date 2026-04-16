from django.shortcuts import render,redirect
from .models import Category
from .models import Dish
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .utils import get_lat_long, calculate_distance
from .models import Cart   # capital C
from django.contrib.auth import logout
from django.shortcuts import redirect

def index(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        people = request.POST.get('people')
        request_text = request.POST.get('request')

        # 🔒 Validation
        if not phone:
            messages.error(request, "Phone number is required!")
            return redirect('index')

        # 1. Save to DB
        try:
            Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                date=date,
                time=time,
                people=people,
                special_request=request_text
            )
        except Exception as e:
            print("DB Error:", e)
            messages.error(request, "❌ Booking failed. Please try again.")
            return redirect('index')

        # 2. Email to ADMIN
        try:
            send_mail(
                subject="🍽️ New Table Booking Received",
                message=f"""
New booking details:

Name: {name}
Email: {email}
Phone: {phone}

Date: {date}
Time: {time}
People: {people}

Special Request:
{request_text}
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print("Admin Email Error:", e)

        # 3. Email to USER
        try:
            send_mail(
                subject="✅ Your Table Booking is Confirmed!",
                message=f"""
Dear {name},

Thank you for choosing our restaurant! 🍽️

📅 Date: {date}
⏰ Time: {time}
👥 Guests: {people}

We look forward to serving you!

Best Regards,  
HEADQUARTER Team
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print("User Email Error:", e)

        messages.success(request, "✅ Booking successful! Confirmation email sent.")
        return redirect('home')

    # ✅ GET → Page load
    categories = Category.objects.prefetch_related('dish_set')
    return render(request, 'index.html', {'categories': categories})

def about(request):
    return render(request, 'about.html')

def service(request):
    return render(request, 'service.html')

def menu(request):
    categories = Category.objects.prefetch_related('dish_set')
    return render(request, 'menu.html', {'categories': categories})

def team(request):
    return render(request, 'team.html')

def shop(request):
    return render(request, 'shop.html')

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for dish_id, quantity in cart.items():
        dish = Dish.objects.get(id=dish_id)

        items.append({
            'dish': dish,
            'quantity': quantity,
            'subtotal': dish.price * quantity
        })

        total += dish.price * quantity

    return render(request, 'shoping-cart.html', {
        'items': items,
        'total': total
    })



@login_required
def add_to_cart_ajax(request, dish_id):
    cart = request.session.get('cart', {})

    if str(dish_id) in cart:
        cart[str(dish_id)] += 1
    else:
        cart[str(dish_id)] = 1

    request.session['cart'] = cart

    return JsonResponse({
        'status': 'success',
        'cart_count': sum(cart.values())
    })
# ➕ Increase Quantity
def increase_quantity(request, dish_id):
    cart = request.session.get('cart', {})

    if str(dish_id) in cart:
        cart[str(dish_id)] += 1

    request.session['cart'] = cart
    return redirect('cart')


# ➖ Decrease Quantity
def decrease_quantity(request, dish_id):
    cart = request.session.get('cart', {})

    if str(dish_id) in cart:
        cart[str(dish_id)] -= 1

        if cart[str(dish_id)] <= 0:
            del cart[str(dish_id)]

    request.session['cart'] = cart
    return redirect('cart')


# ❌ Remove Item
def remove_from_cart(request, dish_id):
    cart = request.session.get('cart', {})

    if str(dish_id) in cart:
        del cart[str(dish_id)]

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def update_cart(request, dish_id, action):
    cart = request.session.get('cart', {})

    dish_id = str(dish_id)

    if dish_id in cart:
        if action == 'increase':
            cart[dish_id] += 1

        elif action == 'decrease':
            cart[dish_id] -= 1
            if cart[dish_id] <= 0:
                del cart[dish_id]

        elif action == 'remove':
            del cart[dish_id]

    request.session['cart'] = cart

    return JsonResponse({'status': 'updated'})

def wishlist(request):
    return render(request, 'wisslist.html')

def main_page(request):
    return render(request, 'main.html')

@login_required
def add_to_cart(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session['cart'] = cart

    return redirect('menu')

from django.shortcuts import render, redirect
from .models import Dish, Order, OrderItem
from django.contrib import messages

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request,'Cart is empty!, Please select items')
        return redirect('cart') 

    items = []
    total = 0
    # User profile se data lena (Auto-fill ke liye)
    profile = getattr(request.user, 'profile', None) 

    for dish_id, quantity in cart.items():
        dish = Dish.objects.get(id=dish_id)
        items.append({
            'dish': dish,
            'quantity': quantity,
            'subtotal': dish.price * quantity
        })
        total += dish.price * quantity

    delivery_fee = 0
    distance = 0
    grand_total = total

    if request.method == "POST":
        address = request.POST.get("address")
        phone = request.POST.get("phone") # Form se phone number lena

        # ... (Aapka distance calculation logic yahan rahega) ...
        # Calculation ke baad:
        
        # 1. Order Create Karein
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=grand_total # Make sure delivery fee added hai
        )

        # 2. Order Items Save Karein
        for item in items:
            OrderItem.objects.create(
                order=order,
                dish=item['dish'],
                quantity=item['quantity']
            )

        # 3. Cart Khali Karein
        request.session['cart'] = {}
        
        messages.success(request, "Order Placed Successfully! 🎉")
        return redirect('my_orders')

    return render(request, "checkout.html", {
        "items": items,
        "total": total,
        "delivery_fee": delivery_fee,
        "distance": round(distance, 2),
        "grand_total": round(grand_total, 2),
        "profile": profile # Template ko profile bhejein
    })

def calculate_distance_ajax(request):
    address = request.GET.get('address')

    lat, lng = get_lat_long(address)

    if lat and lng:
        distance = calculate_distance(
            settings.RESTAURANT_LAT,
            settings.RESTAURANT_LNG,
            lat,
            lng
        )

        return JsonResponse({
            'distance': round(distance, 2),
            'status': 'success'
        })

    return JsonResponse({'status': 'error'})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'my_order.html', {'orders': orders})

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        # Template se data form mein jayega
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate (Custom backend apne aap email/username check kar lega)
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')  # 'home' ki jagah apne home page ka name likho
            else:
                messages.error(request, "Invalid username or password.")
        else:
            # Form invalid hai (errors template mein show honge)
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # User create
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            # Profile create
            Profile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
            )
            messages.success(request, "Registraion successfully!")
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def user_logout(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        return redirect('home') # 'home' aapke URL ka name hai
    
from django.shortcuts import render, redirect
from .models import Booking
from django.contrib import messages

def booking(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        people = request.POST.get('people')
        request_text = request.POST.get('request')

        # 1. Save to DB
        try:
            Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                date=date,
                time=time,
                people=people,
                special_request=request_text
            )
        except Exception as e:
            print("DB Error:", e)
            messages.error(request, "❌ Booking failed. Please try again.")
            return redirect('booking')

        # 2. Send Email to ADMIN
        try:
            send_mail(
                subject="🍽️ New Table Booking Received",
                message=f"""
New booking details:

Name: {name}
Email: {email}
Phone: {phone}

Date: {date}
Time: {time}
People: {people}

Special Request:
{request_text}
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print("Admin Email Error:", e)

        # 3. Send Confirmation Email to USER (Professional Touch 🔥)
        try:
            send_mail(
                subject="✅ Your Table Booking is Confirmed!",
                message=f"""
Dear {name},

Thank you for choosing our restaurant! 🍽️

Your table booking has been successfully received. Here are your booking details:

📅 Date: {date}
⏰ Time: {time}
👥 Guests: {people}

We are excited to serve you and make your experience memorable.

If you have any changes, feel free to reply to this email or contact us.

Best Regards,  
HEADQUARTER Restaurant Team
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print("User Email Error:", e)

        messages.success(request, "✅ Your table has been booked successfully! Confirmation email sent.")
        return redirect('booking')

    return render(request, 'booking.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from .models import Contact
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from .models import Contact  # Ensure your model name is correct

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # 1. Save to Database
        try:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        except Exception as e:
            print("DB Error:", e)
            messages.error(request, "Database error: Could not save your message.")
            return redirect('contact')

        # 2. Send Email (USE send_mail - stable)
        try:
            send_mail(
                subject=f"New Website Inquiry: {subject}",
                message=f"""
You have received a new message:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            messages.success(request, "✅ Message sent successfully!")

        except Exception as e:
            print("Email Error:", e)
            messages.warning(request, "⚠ Message saved, but email failed!")

        return redirect('contact')

    return render(request, 'contact.html')