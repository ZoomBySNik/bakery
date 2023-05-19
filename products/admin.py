from django.contrib import admin
from django.apps import apps
#from .models import Вот тут
# Register your models here.
app_config = apps.get_app_config('products')

#Те модели которые не нужно регистрировать!!! Их нужно импортнуть отдельно
NOT_REGISTERED_MODELS = []
for model in app_config.get_models():
    if not (model in NOT_REGISTERED_MODELS):
        admin.site.register(model)