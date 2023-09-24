from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Recipes)
admin.site.register(models.UserInfo)
admin.site.register(models.BodyInfo)
admin.site.register(models.BodyInfoHistory)
admin.site.register(models.DailyMealPlan)
admin.site.register(models.CustomMealPlan)
admin.site.register(models.UserPreferences)
admin.site.register(models.Last_ingredients)
