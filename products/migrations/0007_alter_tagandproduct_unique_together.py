# Generated by Django 4.2.1 on 2023-05-14 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_tags_alter_tagandproduct_table'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tagandproduct',
            unique_together={('product', 'tag')},
        ),
    ]