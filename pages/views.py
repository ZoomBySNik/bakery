from django.shortcuts import render, redirect
from django.db.models import Count, Subquery, OuterRef, Max
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import render_to_string
from products.models import *
from .forms import *
from django.db.models import F
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.core import serializers
# Create your views here.


def home_view(request, *args, **kwargs):
    print(*args, **kwargs)
    topics = Tag.objects.all()
    orders = get_popular(6).annotate(price=F('pricelistposition__price'))
    response = {
        'orders': orders,
    }
    response = response | context_for_navbar(request)

    return render(request, "home.html", response)


def product_list(request, *args, **kwargs):
    orders = get_popular(None).annotate(price=F('pricelistposition__price'))
    search_query = request.GET.get('search')
    form = FilterForProducts(request.GET)
    tags = request.GET.getlist('tags')
    if form.is_valid():
        if form.cleaned_data["min_price"]:
            min_price = Decimal(form.cleaned_data["min_price"])
            orders = orders.filter(price__gte=min_price)
        if form.cleaned_data["max_price"]:
            max_price = Decimal(form.cleaned_data["max_price"])
            orders = orders.filter(price__lte=max_price)
        if form.cleaned_data["tags"]:
            for tag in tags:
                orders = orders.filter(tagandproduct__tag__id=tag)
        if search_query:
            orders = orders.filter(title__icontains=search_query)
        if 'reset' in request.GET:
            return redirect('product_list')

    print(*args, **kwargs)
    topics = Tag.objects.all()
    products_count = Product.objects.count()
    products_count_filtered = orders.count()
    response = {
        'orders': orders,
        'products_count': products_count,
        'form': form,
        'products_count_filtered': products_count_filtered,
    }
    response = response | context_for_navbar(request)

    return render(request, "products/list_of_products.html", response)


def topic(request, topic_id):
    topic = get_object_or_404(Tag, id=topic_id)
    orders = get_popular(None).annotate(price=F('pricelistposition__price'))
    orders = orders.filter(tagandproduct__tag__id=topic.id)
    topics = Tag.objects.all()
    response = {
        'orders': orders,
        'topic': topic,
    }
    response = response | context_for_navbar(request)
    return render(request, "products/topic_list.html", response)


def get_popular(count):

    #Делаем выборку продуктов
    popular_products = Product.objects.annotate(
        total_orders=Count('pricelistposition__orderposition__order', distinct=True)
    ).order_by('-total_orders')[:count]

    # Определяем актуальную цену
    latest_price_list_id = PriceList.objects.aggregate(latest_id=Max('id'))['latest_id']
    latest_prices = PriceListPosition.objects.filter(price_list_id=latest_price_list_id).select_related('product')
    for product in popular_products:
        product.latest_price = latest_prices.get(product=product).price
    return popular_products


def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')  # Перенаправление на главную страницу после успешной регистрации
    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def add_to_cart(request, product_id):
    cart = request.COOKIES.get('cart', '')
    ids = cart.split(',')
    target_id = product_id
    processed_ids = []
    found = False
    for id_str in ids:
        if id_str.startswith(str(target_id) + "k"):
            found = True
            parts = id_str.split("k")
            if len(parts) == 2:
                try:
                    num = int(parts[1])
                    num += 1
                    id_str = parts[0] + "k" + str(num)
                except ValueError:
                    pass
        processed_ids.append(id_str)

    if not found:
        processed_ids.append(str(target_id) + "k1")

    output_string = ','.join(processed_ids)
    cart = output_string
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('cart', cart)
    return response


def substract_from_cart(request, product_id):
    cart = request.COOKIES.get('cart', '')
    target_id = product_id
    ids = cart.split(',')
    processed_ids = []
    for id_str in ids:
        if id_str.startswith(str(target_id) + "k"):
            parts = id_str.split("k")
            if len(parts) == 2:
                try:
                    num = int(parts[1])
                    num -= 1
                    if num > 0:
                        id_str = parts[0] + "k" + str(num)
                    else:
                        continue
                except ValueError:
                    pass
        processed_ids.append(id_str)

    output_string = ",".join(processed_ids)
    cart = output_string
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('cart', cart)
    return response


def cart(request):
    cart = request.COOKIES.get('cart', '')
    payment_types = TypeOfPayment.objects.all()
    if cart:
        product_ids_counts = cart.split(',')
        product_ids = []
        counts = []
        for pair in product_ids_counts:
            parts = pair.split('k')
            if len(parts) == 2:
                try:
                    id_value = int(parts[0])
                    count_value = int(parts[1])
                    product_ids.append(id_value)
                    counts.append(count_value)
                except ValueError:
                    pass
        latest_price_list_id = PriceList.objects.aggregate(latest_id=Max('id'))['latest_id']
        products = PriceListPosition.objects.filter(price_list_id=latest_price_list_id).filter(id__in=product_ids)
        for product in products:
            product.count = counts[product_ids.index(product.id)] if product.id in product_ids else 0
        total_price = sum(product.price*product.count for product in products)

    context = {
        'products': products,
        'total_price': total_price,
        'payment_types': payment_types,
    }
    context = context | context_for_navbar(request)

    return render(request, 'cart.html', context)


def checkout(request):
    payment_types = TypeOfPayment.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Обработка данных формы и создание заказа
            # ...
            # После успешного создания заказа, очищаем корзину
            response = redirect('cart')
            response.delete_cookie('cart')
            return response
    else:
        form = OrderForm()

    context = {
        'form': form,
        'payment_types': payment_types,
    }
    context = context | context_for_navbar(request)
    return render(request, 'checkout.html', context)


def context_for_navbar(request):
    cart = request.COOKIES.get('cart', '')
    topics = Tag.objects.all()
    return {'cart': cart, 'topics': topics}
