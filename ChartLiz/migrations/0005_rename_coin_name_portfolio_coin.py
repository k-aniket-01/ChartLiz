# Generated by Django 5.1.2 on 2025-04-10 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ChartLiz', '0004_portfolio_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolio',
            old_name='coin_name',
            new_name='coin',
        ),
    ]
