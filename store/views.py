from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from django.conf import settings  # ADD THIS LINE
import decimal

from .models import Address, Cart, Category, Order, Product
from .forms import RegistrationForm, AddressForm


def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    return render(request, 'store/index.html', {
        'categories': categories,
        'products': products,
    })


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(
        is_active=True,
        category=product.category
    )
    return render(request, 'store/detail.html', {
        'product': product,
        'related_products': related_products,
    })


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories': categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products,
        'categories': categories,
    })


# ---------- AUTH ----------

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
        return render(request, 'account/register.html', {'form': form})


@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {
        'addresses': addresses,
        'orders': orders
    })


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            Address.objects.create(
                user=request.user,
                locality=form.cleaned_data['locality'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
            )
            messages.success(request, "Address added successfully.")
        return redirect('store:profile')


@login_required
def add_to_cart(request):
    product = get_object_or_404(Product, id=request.GET.get('prod_id'))
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart.quantity += 1
        cart.save()
    return redirect('store:cart')


@login_required
def cart(request):
    cart_products = Cart.objects.filter(user=request.user)
    amount = sum(p.quantity * p.product.price for p in cart_products)
    shipping_amount = decimal.Decimal(10)

    return render(request, 'store/cart.html', {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': Address.objects.filter(user=request.user),
    })


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('store:cart')

    # calculate totals
    amount = 0
    cart_data = []
    for item in cart_items:
        line = item.quantity * item.product.price
        amount += line
        cart_data.append({
            'product': item.product,
            'quantity': item.quantity,
            'line_total': line
        })

    shipping = decimal.Decimal(10)
    total = amount + shipping

    if request.method == "POST":
        saved_addr_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # NEW ADDRESS
        new_locality = request.POST.get('locality')
        new_city = request.POST.get('city')
        new_state = request.POST.get('state')

        # Choose saved address OR create a new one
        if saved_addr_id:
            address = get_object_or_404(Address, id=saved_addr_id, user=request.user)
        else:
            if not(new_locality and new_city and new_state):
                messages.error(request, "Please fill all fields for new address.")
                return redirect('store:checkout')

            address = Address.objects.create(
                user=request.user,
                locality=new_locality,
                city=new_city,
                state=new_state
            )

        # Handle payment proof for QR payment
        payment_proof = None
        if payment_method == "QR":
            payment_proof = request.FILES.get('payment_proof')
            if not payment_proof:
                messages.error(request, "Please upload your payment screenshot for QR payment.")
                return redirect('store:checkout')
            
            # Validate file size (max 5MB)
            if payment_proof.size > 5 * 1024 * 1024:
                messages.error(request, "Payment proof image is too large. Maximum size is 5MB.")
                return redirect('store:checkout')
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if payment_proof.content_type not in allowed_types:
                messages.error(request, "Invalid file type. Please upload a valid image (JPG, PNG, or WEBP).")
                return redirect('store:checkout')

        # Create orders for each cart item
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                address=address,
                product=item.product,
                quantity=item.quantity,
                payment_method=payment_method,
                payment_proof=payment_proof,
                payment_status='Pending' if payment_method == 'QR' else 'Verified'
            )
            item.delete()

        if payment_method == "QR":
            messages.success(
                request, 
                "Order placed successfully! Your payment is under review. "
                "You will be notified once the admin verifies your payment."
            )
        else:
            messages.success(request, "Order placed successfully! Pay on delivery.")

        return redirect('store:orders')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_data,
        'addresses': addresses,
        'amount': amount,
        'shipping_amount': shipping,
        'total_amount': total,
    })


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': orders})


def shop(request):
    return render(request, 'store/shop.html')


def test(request):
    return render(request, 'store/test.html')

@login_required
def remove_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Product removed from cart.")
    return redirect('store:cart')

@login_required
def plus_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('store:cart')

@login_required
def minus_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if cart_item.quantity == 1:
        cart_item.delete()
    else:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect('store:cart')

@login_required
def remove_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Address removed successfully.")
    return redirect('store:profile')
def order_receipt(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = [{
        'product': order.product,
        'quantity': order.quantity,
        'total_price': order.total_amount
    }]
    return render(request, 'store/order_receipt.html', {
        'order': order,
        'order_items': order_items
    })