# Generated by Django 5.1.3 on 2024-11-30 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0006_remove_purchasereturn_remarks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='serial_numbers',
            field=models.TextField(blank=True, null=True),
        ),
    ]