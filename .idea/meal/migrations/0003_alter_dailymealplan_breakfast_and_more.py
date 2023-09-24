# Generated by Django 4.2.4 on 2023-09-21 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0002_custommealplan_remove_weeklymealplan_day1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailymealplan',
            name='breakfast',
            field=models.ManyToManyField(blank=True, null=True, related_name='breakfast_meals', to='meal.recipes'),
        ),
        migrations.AlterField(
            model_name='dailymealplan',
            name='dinner',
            field=models.ManyToManyField(blank=True, null=True, related_name='dinner_meals', to='meal.recipes'),
        ),
        migrations.AlterField(
            model_name='dailymealplan',
            name='lunch',
            field=models.ManyToManyField(blank=True, null=True, related_name='lunch_meals', to='meal.recipes'),
        ),
    ]
