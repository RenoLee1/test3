from django.db import models

# Create your models here.
class UserInfo(models.Model):
    user_name = models.CharField(verbose_name='Username', max_length=64)
    email = models.EmailField(verbose_name='Email', max_length=256)
    password = models.CharField(verbose_name='password', max_length=64)

class BodyInfo(models.Model):
    height = models.CharField(verbose_name='身高', max_length=64)
    weight = models.CharField(verbose_name='体重', max_length=64)
    age = models.IntegerField(verbose_name="年龄")

    gender_choices = (
        (1, "male"),
        (2, "female"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices, default=1)

    user_id = models.ForeignKey(to='UserInfo', to_field="id", on_delete=models.CASCADE)

