from django import forms
from products.models import Tag


class FilterForProducts(forms.Form):
    min_price = forms.IntegerField(label='от', required=False)
    max_price = forms.IntegerField(label='до', required=False)
    tags = forms.MultipleChoiceField(label='фильтры', widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].choices = [(tag.id, tag.title) for tag in Tag.objects.all()]
