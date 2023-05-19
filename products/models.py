from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, null=False, blank=False, verbose_name='Заказчик')
    date_of_delivery = models.DateField(null=False, blank=False, verbose_name='Дата доставки')
    time_of_order = models.DateTimeField(null=False, blank=False, auto_now_add=True, editable=False,
                                         verbose_name='Время заказа')
    address_of_delivery = models.CharField(null=False, blank=False, max_length=128, verbose_name='Адрес доставки')
    total_price = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2,
                                      verbose_name='Итоговая стоимость')
    type_of_payment = models.ForeignKey('TypeOfPayment', on_delete=models.PROTECT, null=False, blank=False,
                                        verbose_name='Тип оплаты')
    commentary_for_order = models.TextField(null=True, blank=True, verbose_name='Комментарий к заказу')

    def __str__(self):
        return '%s %s %s' % (self.customer, self.date_of_delivery, self.total_price)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class TypeOfPayment(models.Model):
    name = models.CharField(max_length=32, verbose_name='Тип оплаты')

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = 'Типы оплаты'
        verbose_name_plural = 'Типы оплаты'


class OrderAndState(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Заказ')
    state_of_order = models.ForeignKey('StateOfOrder', on_delete=models.CASCADE, null=False, blank=False,
                                       verbose_name='Статус заказа')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Работник')

    def __str__(self):
        return '%s %s %s' % (self.order.customer, self.state_of_order, self.employee)

    class Meta:
        verbose_name = 'Заказ и статус'
        verbose_name_plural = 'Заказы и статусы'


class StateOfOrder(models.Model):
    name = models.CharField(null=False, blank=False, max_length=32, verbose_name='Статус заказа')

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'


class OrderPosition(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Заказ')
    price_list_position = models.ForeignKey('PriceListPosition', on_delete=models.CASCADE, null=False, blank=False,
                                            verbose_name='Продукт')
    count_of_products = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2,
                                            verbose_name='Количество')
    price_of_position = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2,
                                            verbose_name='Стоимость позиции')

    def __str__(self):
        return '%s %s %s %s' % (self.order, self.price_list_position, self.count_of_products, self.price_of_position)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'


class PriceList(models.Model):
    approval_date = models.DateField(null=False, blank=False, auto_now_add=True,
                                     verbose_name='Дата утверждения прайс-листа')

    def __str__(self):
        return '%s' % (self.approval_date)

    class Meta:
        verbose_name = 'Прайс-лист'
        verbose_name_plural = 'Прайс-листы'


class PriceListPosition(models.Model):
    price_list = models.ForeignKey('PriceList', on_delete=models.CASCADE, null=False, blank=False,
                                   verbose_name='Прайс-лист')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Продукт')
    price = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2, verbose_name='Цена')
    units = models.CharField(null=False, blank=False, max_length=32, verbose_name='Единица измерения')

    def __str__(self):
        return '%s %s %s' % (self.price_list, self.product, self.price)

    class Meta:
        verbose_name = 'Позиция прайс-листа'
        verbose_name_plural = 'Позиции прайс-листов'


class Product(models.Model):
    title = models.CharField(max_length=64, null=False, blank=False, verbose_name='Наименование')
    description = models.TextField(verbose_name='Описание')
    weight = models.IntegerField(null=False, blank=False, verbose_name='Вес (гр.)')
    image = models.ImageField(null=True, blank=True, upload_to='products_img/')
    tags = models.ManyToManyField('Tag', verbose_name='Теги')

    def __str__(self):
        return '%s' % (self.title)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class TagAndProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Продукт')
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=False, blank=False, verbose_name='Тег')

    def __str__(self):
        return '%s %s' % (self.product, self.tag)

    class Meta:
        db_table = 'products_product_tag'
        verbose_name = 'Тег и продукт'
        verbose_name_plural = 'Теги и продукты'
        unique_together = ('product', 'tag')


class Tag(models.Model):
    title = models.CharField(max_length=64, null=False, blank=False, verbose_name='Наименование для тега')
    title_for_topic = models.CharField(max_length=64, null=True, blank=True, verbose_name='Наименование')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    board_image = models.ImageField(null=True, blank=True, upload_to='tags_img/board')
    icon_image = models.ImageField(null=True, blank=True, upload_to='tags_img/icon')

    def __str__(self):
        return '%s' % (self.title)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Customer(User):
    phone_number = models.CharField(max_length=18, null=False, blank=False, verbose_name='Номер телефона')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Employee(User):
    date_of_employment = models.DateField(null=False, blank=False, verbose_name='Дата приема на работу')
    date_of_dismissal = models.DateField(null=True, blank=True, verbose_name='Дата увольнения')
    employees_position = models.CharField(max_length=32, null=True, blank=True, verbose_name='Должность')

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = 'Работники'
