# Generated by Django 5.0.6 on 2024-10-17 21:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField()),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('cost_price', models.DecimalField(decimal_places=2, help_text='example: 500.50', max_digits=10)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_batch', to='test2.product')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units_sold', models.PositiveIntegerField()),
                ('unit_type', models.CharField(max_length=50)),
                ('profit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2.product')),
            ],
        ),
        migrations.CreateModel(
            name='UnitMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(max_length=50)),
                ('unit_selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_measurements', to='test2.product')),
            ],
        ),
    ]