# Generated by Django 4.2.4 on 2023-09-22 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0005_recipes_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dietary_requirements', models.TextField(blank=True, null=True, verbose_name='饮食要求')),
                ('fitness_goal', models.TextField(blank=True, null=True, verbose_name='健身目标')),
                ('taste_preference', models.TextField(blank=True, null=True, verbose_name='口味偏好')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='meal.userinfo')),
            ],
        ),
    ]
