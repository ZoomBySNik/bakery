from django.shortcuts import render, redirect
from django.db.models import Count, Subquery, OuterRef, Max
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import *
from .forms import *
from django.db.models import F
from decimal import Decimal
from django.shortcuts import get_object_or_404
# Create your views here.


def home_view(request, *args, **kwargs):
    print(*args, **kwargs)
    topics = Tag.objects.all()
    orders = get_popular(6).annotate(price=F('pricelistposition__price'))
    response = {
        'orders': orders,
        'topics': topics,
    }

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
        'topics': topics,
        'products_count': products_count,
        'form': form,
        'products_count_filtered': products_count_filtered,
    }

    return render(request, "products/list_of_products.html", response)


def topic(request, topic_id):
    topic = get_object_or_404(Tag, id=topic_id)
    orders = get_popular(None).annotate(price=F('pricelistposition__price'))
    orders = orders.filter(tagandproduct__tag__id=topic.id)
    topics = Tag.objects.all()
    response = {
        'orders': orders,
        'topic': topic,
        'topics': topics,

    }
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