from django.db import models

# Create your models here.
class UserInfo(models.Model):
    user_name = models.CharField(verbose_name='Username', max_length=64)
    email = models.EmailField(verbose_name='Email', max_length=256)
    password = models.CharField(verbose_name='password', max_length=64)

class BodyInfo(models.Model):
    height = models.DecimalField(verbose_name='身高', max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(verbose_name='体重', max_digits=5, decimal_places=2, blank=True, null=True)
    age = models.IntegerField(verbose_name="年龄", null=True, blank=True)
    bmi = models.DecimalField(verbose_name='BMI', max_digits=5, decimal_places=2, default=0.0, null=True, blank=True)
    bodyfat = models.DecimalField(verbose_name='Body Fat', max_digits=5, decimal_places=2, default=None, null=True, blank=True)
    gender_choices = (
        (1, "male"),
        (2, "female"), 
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices, default=1)

    user = models.ForeignKey(to='UserInfo', to_field="id", on_delete=models.CASCADE, related_name='body_info', null=False, blank=False)

    def save(self, *args, **kwargs):
        # 如果height和weight都不是null，则计算bmi
        if self.height is not None and self.weight is not None:
            self.bmi = (self.weight / ((self.height / 100) ** 2))
        super().save(*args, **kwargs)
        # Create a new history record
        BodyInfoHistory.objects.create(
        body_info=self,
        weight=self.weight,
        bmi=self.bmi,
        bodyfat=self.bodyfat,
    )


class BodyInfoHistory(models.Model):
    body_info = models.ForeignKey(BodyInfo, on_delete=models.CASCADE, related_name='history')
    weight = models.DecimalField(verbose_name='体重', max_digits=5, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(verbose_name='BMI', max_digits=5, decimal_places=2, null=True, blank=True)
    bodyfat = models.DecimalField(verbose_name='Body Fat', max_digits=5, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Recipes(models.Model):
    name = models.CharField(verbose_name='Recipename', max_length=255)
    calories = models.CharField(verbose_name='CalorieValue', max_length=64)
    fat = models.DecimalField(verbose_name='Fat', max_digits=8, decimal_places=2, blank=False)
    protein = models.DecimalField(verbose_name='Protein', max_digits=8, decimal_places=2, blank=False, null=False, default=0)
    carbohydrate = models.DecimalField(verbose_name='Carbohydrate', max_digits=8, decimal_places=2, blank=False, null=False, default=0)
    introduction = models.TextField(verbose_name='introduction')

    def __str__(self):
        return str(self.name)

class DailyMealPlan(models.Model):
    user = models.ForeignKey(UserInfo, verbose_name='User', on_delete=models.CASCADE, related_name='daily_meal_plans')
    breakfast = models.ManyToManyField(Recipes, related_name='breakfast_meals', blank=True)
    lunch = models.ManyToManyField(Recipes, related_name='lunch_meals', blank=True)
    dinner = models.ManyToManyField(Recipes, related_name='dinner_meals', blank=True)
    date = models.DateField(verbose_name='Date')

    def __str__(self):
        return str(self.date)


class WeeklyMealPlan(models.Model):
    user = models.ForeignKey(UserInfo, verbose_name='User', on_delete=models.CASCADE, related_name='weekly_meal_plans')
    day1 = models.ForeignKey(DailyMealPlan, related_name='monday_meals', on_delete=models.CASCADE)
    day2 = models.ForeignKey(DailyMealPlan, related_name='tuesday_meals', on_delete=models.CASCADE)
    day3 = models.ForeignKey(DailyMealPlan, related_name='wednesday_meals', on_delete=models.CASCADE)
    day4 = models.ForeignKey(DailyMealPlan, related_name='thursday_meals', on_delete=models.CASCADE)
    day5 = models.ForeignKey(DailyMealPlan, related_name='friday_meals', on_delete=models.CASCADE)
    day6 = models.ForeignKey(DailyMealPlan, related_name='saturday_meals', on_delete=models.CASCADE)
    day7 = models.ForeignKey(DailyMealPlan, related_name='sunday_meals', on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')

    def __str__(self):
        return f"From {self.start_date} to {self.end_date}"

class MonthlyMealPlan(models.Model):
    user = models.ForeignKey(UserInfo, verbose_name='User', on_delete=models.CASCADE, related_name='monthly_meal_plans')
    week1 = models.ForeignKey(WeeklyMealPlan, related_name='first_week_meals', on_delete=models.CASCADE)
    week2 = models.ForeignKey(WeeklyMealPlan, related_name='second_week_meals', on_delete=models.CASCADE)
    week3 = models.ForeignKey(WeeklyMealPlan, related_name='third_week_meals', on_delete=models.CASCADE)
    week4 = models.ForeignKey(WeeklyMealPlan, related_name='fourth_week_meals', on_delete=models.CASCADE)
    week5 = models.ForeignKey(WeeklyMealPlan, related_name='fifth_week_meals', on_delete=models.CASCADE, null=True, blank=True)
    month = models.CharField(verbose_name='Month', max_length=20)
    year = models.PositiveIntegerField(verbose_name='Year')

    def __str__(self):
        return f"{self.month} {self.year}"
