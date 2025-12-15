from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
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

    # Calculate totals
    amount = 0
    cart_data = []
    for item in cart_items:
        line_total = item.quantity * item.product.price
        amount += line_total
        cart_data.append({
            'product': item.product,
            'quantity': item.quantity,
            'line_total': line_total,
        })

    shipping_amount = decimal.Decimal(10)
    total_amount = amount + shipping_amount

    if request.method == 'POST':
        address_id = request.POST.get('address')

        # ✅ IMPORTANT VALIDATION
        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('store:checkout')

        address = get_object_or_404(
            Address,
            id=int(address_id),
            user=request.user
        )

        # Create orders
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                address=address,
                product=item.product,
                quantity=item.quantity
            )
            item.delete()

        messages.success(request, "Order placed successfully! Pay on delivery.")
        return redirect('store:orders')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_data,
        'addresses': addresses,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
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

