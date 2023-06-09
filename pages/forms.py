from django import forms
from products.models import *
from django.contrib.auth.forms import UserCreationForm


class FilterForProducts(forms.Form):
    min_price = forms.IntegerField(label='Цена от', required=False)
    max_price = forms.IntegerField(label='Цена до', required=False)
    tags = forms.MultipleChoiceField(label='Разделы', widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].choices = [(tag.id, tag.title) for tag in Tag.objects.all()]


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Имя')
    last_name = forms.CharField(max_length=30, label='Фамилия')
    phone_number = forms.CharField(max_length=18, label='Номер телефона')

    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = UserCreationForm.Meta.fields + ('phone_number', 'first_name', 'last_name')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['date_of_delivery', 'address_of_delivery', 'type_of_payment', 'commentary_for_order']