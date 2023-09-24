from django.test import TestCase
from django.test import TestCase
from django.contrib.auth.models import User
from meal.models import BodyInfo, UserInfo, Recipes, DailyMealPlan, WeeklyMealPlan, MonthlyMealPlan
# Create your tests here.

class Test_Create(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_userInfo_1 = UserInfo.objects.create(
            user_name='reno',
            email='a@a.com',
            password='123'
        )

        test_BodyInfo = BodyInfo.objects.create(
            height='175cm',
            weight='80kg',
            age=20,
            gender=1,
            user_id=1
        )

        test_recipe = Recipes.objects.create(
            name='EggTomato',
            calories='1234',
            fat='54g',
            introduction='my new recipe'
        )

        test_recipe2 = Recipes.objects.create(
            name='BeefTomato',
            calories='1235',
            fat='60g',
            introduction='my second recipe'
        )

        test_recipe3 = Recipes.objects.create(
            name='SuperTomato',
            calories='1236',
            fat='900g',
            introduction='my third recipe'
        )

        test_daily_meal_plan = DailyMealPlan.objects.create(
            user=test_userInfo_1,
            date='2020-09-16'
        )

        test_weekly_meal_plan = WeeklyMealPlan.objects.create(
            user=test_userInfo_1,
            day1=test_daily_meal_plan,
            day2=test_daily_meal_plan,
            day3=test_daily_meal_plan,
            day4=test_daily_meal_plan,
            day5=test_daily_meal_plan,
            day6=test_daily_meal_plan,
            day7=test_daily_meal_plan,
            start_date='2020-08-16',
            end_date='2020-08-23'
        )

        test_monthly_meal_plan = MonthlyMealPlan.objects.create(
            user=test_userInfo_1,
            week1=test_weekly_meal_plan,
            week2=test_weekly_meal_plan,
            week3=test_weekly_meal_plan,
            week4=test_weekly_meal_plan,
            month='8',
            year='2020'
        )

        test_daily_meal_plan.breakfast.set([test_recipe])
        test_daily_meal_plan.lunch.set([test_recipe2])
        test_daily_meal_plan.dinner.set([test_recipe3])

    def test_user_content(self):

        # 构建测试模型
        body_info = BodyInfo.objects.get(id=1)
        user_info = UserInfo.objects.get(id=1)
        recipe = Recipes.objects.get(id=1)
        daily_meal_plan = DailyMealPlan.objects.get(id=1)
        weekly_meal_plan = WeeklyMealPlan.objects.get(id=1)
        monthly_meal_plan = MonthlyMealPlan.objects.get(id=1)

        # 测试userinfo
        user_name = f'{user_info.user_name}'
        email = f'{user_info.email}'
        password = f'{user_info.password}'

        self.assertEqual(user_name, 'reno')
        self.assertEqual(email, 'a@a.com')
        self.assertEqual(password, '123')

        # 测试BodyInfo
        height = f'{body_info.height}'
        weight = f'{body_info.weight}'
        age = f'{body_info.age}'
        gender = f'{body_info.gender}'

        self.assertEqual(height, '175cm')
        self.assertEqual(weight, '80kg')
        self.assertEqual(age, '20')
        self.assertEqual(gender, '1')

        # 测试Recipe
        recipe_name = f'{recipe.name}'
        recipe_calories = f'{recipe.calories}'
        recipe_fat = f'{recipe.fat}'
        recipe_introduction = f'{recipe.introduction}'

        self.assertEqual(recipe_name, 'EggTomato')
        self.assertEqual(recipe_calories, '1234')
        self.assertEqual(recipe_fat, '54g')
        self.assertEqual(recipe_introduction, 'my new recipe')
        self.assertEqual(str(recipe), recipe_name)

        # 测试DailyMealPlan
        daily_user_name = f'{daily_meal_plan.user}'
        self.assertEqual(str(daily_user_name), 'reno')
        self.assertEqual(daily_meal_plan.breakfast.first(), recipe)
        self.assertEqual(str(daily_meal_plan.lunch.first()), 'BeefTomato')
        self.assertEqual(str(daily_meal_plan.dinner.first()), 'SuperTomato')
        self.assertEqual(str(daily_meal_plan), '2020-09-16')
        self.assertEqual(daily_user_name, 'reno')

        # 测试WeeklyMealPlan
        weekly_start_date = f'{weekly_meal_plan.start_date}'
        weekly_end_date = f'{weekly_meal_plan.end_date}'
        weekly_user = f'{weekly_meal_plan.user}'

        self.assertEqual(weekly_start_date, '2020-08-16')
        self.assertEqual(weekly_end_date, '2020-08-23')
        self.assertEqual(str(weekly_meal_plan.day1), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day2), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day3), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day4), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day5), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day6), '2020-09-16')
        self.assertEqual(str(weekly_meal_plan.day7), '2020-09-16')
        self.assertEqual(weekly_user, 'reno')

        # 测试MonthlyMealPlan
        monthly_month = f'{monthly_meal_plan.month}'
        monthly_year = f'{monthly_meal_plan.year}'
        monthly_user = f'{monthly_meal_plan.user}'

        self.assertEqual(monthly_user, 'reno')
        self.assertEqual(str(monthly_meal_plan.week1), 'From 2020-08-16 to 2020-08-23')
        self.assertEqual(str(monthly_meal_plan.week2), 'From 2020-08-16 to 2020-08-23')
        self.assertEqual(str(monthly_meal_plan.week3), 'From 2020-08-16 to 2020-08-23')
        self.assertEqual(str(monthly_meal_plan.week4), 'From 2020-08-16 to 2020-08-23')
        self.assertEqual(monthly_month, '8')
        self.assertEqual(monthly_year, '2020')
        self.assertEqual(str(monthly_meal_plan), '8 2020')







