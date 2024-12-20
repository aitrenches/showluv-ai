# Generated by Django 5.0.6 on 2024-10-17 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='unit_type',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='units_sold',
        ),
        migrations.AddField(
            model_name='productbatch',
            name='remaining_quantity',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='quantity_sold',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sale',
            name='total_cost_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='total_selling_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='cost_price',
            field=models.DecimalField(decimal_places=2, help_text='example: 500.50', max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='quantity',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='profit',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
