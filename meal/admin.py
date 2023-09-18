from django.contrib import admin
from .models import Recipes, UserInfo, BodyInfo
# Register your models here.
admin.site.register(Recipes)
admin.site.register(UserInfo)
admin.site.register(BodyInfo)