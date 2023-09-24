from rest_framework import serializers
from meal import models
from utils.encrypt import md5
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from . import views
from utils.helpfunc import get_user_from_token
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ['id', 'user_name', 'email', 'password']

class BodyInfoSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    bodyfat = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    age = serializers.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    class Meta:
        model = models.BodyInfo
        fields = ['id', 'height', 'weight', 'age', 'gender', 'user', 'bmi', 'bodyfat']


class BodyInfoHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BodyInfoHistory
        fields = ['id', 'body_info', 'weight', 'bmi', 'bodyfat', 'timestamp']





class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'password', 'confirm_password', 'email']
    
    def validate_user_name(self, value):
        if models.UserInfo.objects.filter(user_name=value).exists():
            raise serializers.ValidationError("用户名已被使用")
        return value
    
    def validate_email(self, value):
        if models.UserInfo.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被绑定")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("密码不匹配")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')  # 移除 'confirm_password' 字段
        validated_data['password'] = md5(validated_data['password'])  # 对密码进行加密
        user = models.UserInfo.objects.create(**validated_data)  # 使用验证后的数据创建新的用户
        

        refresh = views.CustomRefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        user.token = token
        return user
    

class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True)


class ForgetPasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'password', 'confirm_password', 'email']


    def validate(self, attrs):
        user_name = attrs.get("user_name")
        email = attrs.get("email")
        new_password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        user_query = models.UserInfo.objects.filter(
            user_name=user_name, email=email)
        if not user_query.exists():
            raise serializers.ValidationError(
                "User does not exist")

        # 获取用户对象
        user = user_query.first()

        # 检查新密码是否与旧密码相同
        if user.password == md5(new_password):
            raise serializers.ValidationError(
                "The new password cannot be the same as the old password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise serializers.ValidationError("Password not the same")
        return attrs



class RecipesSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.id')
    user = serializers.IntegerField(source='user.id', default=None, read_only=True)
    class Meta:
        model = models.Recipes
        fields = ['id', 'name', 'calories', 'fat', 'protein', 'carbohydrate', 'introduction', 'user']

    

class DailyMealPlanSerializer(serializers.ModelSerializer):
    breakfast = RecipesSerializer(many=True, required=False)
    lunch = RecipesSerializer(many=True, required=False)
    dinner = RecipesSerializer(many=True, required=False)
    user = serializers.ReadOnlyField(source='user.id')


    class Meta:
        model = models.DailyMealPlan
        fields = ('id', 'user', 'breakfast', 'lunch', 'dinner', 'date')

    def create(self, validated_data):
        # 获取用户
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("No request object found in serializer context.")
        user = get_user_from_token(request)
        
        if not user or not isinstance(user, models.UserInfo):
            raise serializers.ValidationError("User is not authenticated.")
        
        validated_data['user'] = user
        breakfast_data = validated_data.pop('breakfast', None)
        lunch_data = validated_data.pop('lunch', None)
        dinner_data = validated_data.pop('dinner', None)

        daily_meal_plan = models.DailyMealPlan.objects.create(**validated_data)

        if breakfast_data is not None:
            for breakfast in breakfast_data:
                recipe, created = models.Recipes.objects.get_or_create(**breakfast)
                daily_meal_plan.breakfast.add(recipe)
        else:
            daily_meal_plan.breakfast.set([])

        if lunch_data is not None:
            for lunch in lunch_data:
                recipe, created = models.Recipes.objects.get_or_create(**lunch)
                daily_meal_plan.lunch.add(recipe)
        else:
            daily_meal_plan.lunch.set([])

        if dinner_data is not None:
            for dinner in dinner_data:
                recipe, created = models.Recipes.objects.get_or_create(**dinner)
                daily_meal_plan.dinner.add(recipe)
        else:
            daily_meal_plan.dinner.set([])

        daily_meal_plan.save()
        return daily_meal_plan

    def update(self, instance, validated_data):
        # 使用一个循环来处理breakfast, lunch和dinner，这样可以避免代码重复
        for meal_time in ['breakfast', 'lunch', 'dinner']:
            if meal_time in validated_data:  # 只处理传入的数据
                meal_data = validated_data.pop(meal_time)  # 从validated_data中提取meal data
                meal = getattr(instance, meal_time)  # 获取meal attribute
                meal.clear()  # 清空现有的meal data
                
                for recipe_data in meal_data:  # 通过循环来处理每一个recipe
                    recipe, created = models.Recipes.objects.get_or_create(**recipe_data)
                    meal.add(recipe)
        
        # 更新其它的字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
    # def get_user_from_token(self, request):
    #     # 1. 从请求头中提取JWT Token
    #     header = request.headers.get('Authorization')
    #     if not header:
    #         raise ValueError("No Authorization header provided")

    #     # 2. 解码Token以提取用户ID
    #     token = header.split(' ')[1]
    #     try:
    #         untyped_token = UntypedToken(token)
    #         user_id = untyped_token["user_id"]
    #     except (InvalidToken, TokenError, KeyError):
    #         raise ValueError("Invalid token")

    #     # 3. 使用user_id查询你的UserInfo模型
    #     user_info = models.UserInfo.objects.filter(id=user_id).first()
    #     if not user_info:
    #         raise ValueError("User not found")

    #     return user_info


class CustomMealPlanSerializer(serializers.ModelSerializer):
    daily_plans = DailyMealPlanSerializer(many=True, required=False)
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = models.CustomMealPlan
        fields = '__all__'

    def create(self, validated_data):
        # 获取用户
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("No request object found in serializer context.")
        user = get_user_from_token(request)
        
        if not user or not isinstance(user, models.UserInfo):
            raise serializers.ValidationError("User is not authenticated.")
        
        validated_data['user'] = user
        
        
        
        daily_plans_data = validated_data.pop('daily_plans', [])
        start_date = validated_data.get('start_date')  # 假设你的 CustomMealPlan 模型有一个 start_date 字段
        end_date = validated_data.get('end_date')  # 假设你的 CustomMealPlan 模型有一个 end_date 字段

        custom_meal_plan = models.CustomMealPlan.objects.create(**validated_data)

        existing_dates = [dp['date'] for dp in daily_plans_data if dp.get('date')]  # 从传入数据中获取所有已存在的日期
        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]  # 生成start_date和end_date之间的所有日期

        for day_date in all_dates:
            # 在此日期检查是否已有一个daily meal plan
            daily_plan = models.DailyMealPlan.objects.filter(user=validated_data['user'], date=day_date).first()
            
            if not daily_plan:
                # 如果不存在，则创建一个新的
                daily_plan = models.DailyMealPlan.objects.create(user=validated_data['user'], date=day_date)
            
            if day_date in existing_dates:
                # 如果传入数据中存在该日期的 daily_plan，则获取该daily_plan数据并用该数据创建一个daily_plan
                daily_plan_data = next(dp for dp in daily_plans_data if dp['date'] == day_date)
                daily_plan_serializer = DailyMealPlanSerializer(data=daily_plan_data)
                if daily_plan_serializer.is_valid():
                    daily_plan = daily_plan_serializer.save()
                else:
                    raise ValidationError(daily_plan_serializer.errors)
            
            custom_meal_plan.daily_plans.add(daily_plan)

        custom_meal_plan.save()
        return custom_meal_plan


    def update(self, instance, validated_data):
        daily_plans_data = validated_data.pop('daily_plans')
        
        existing_daily_plans = {dp.id: dp for dp in instance.daily_plans.all()}
        incoming_daily_plans_ids = [dp.get('id') for dp in daily_plans_data if dp.get('id') is not None]
        
        # 删除不再存在的日常餐计划
        for daily_plan_id in set(existing_daily_plans.keys()) - set(incoming_daily_plans_ids):
            instance.daily_plans.remove(existing_daily_plans[daily_plan_id])
        
        # 创建新的或更新现有的日常餐计划
        for daily_plan_data in daily_plans_data:
            daily_plan_id = daily_plan_data.pop('id', None)
            daily_plan_serializer = DailyMealPlanSerializer(
                instance=existing_daily_plans.get(daily_plan_id) if daily_plan_id is not None else None,
                data=daily_plan_data
            )
            if daily_plan_serializer.is_valid():
                daily_plan = daily_plan_serializer.save()
                instance.daily_plans.add(daily_plan)
            else:
                raise ValidationError(daily_plan_serializer.errors)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class UserPreferencesSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.user_name')  # 这会展示关联的用户名称

    class Meta:
        model = models.UserPreferences
        fields = ('id', 'user_name', 'dietary_requirements', 'fitness_goal', 'taste_preference')

class LastIngredientsSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.user_name')
    last_ingredients = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = models.Last_ingredients
        fields = ['id', 'user_name','last_ingredients']

'''OpenAI'''
class GPTRecipeAdviceSerializer(serializers.Serializer):
    request_type = serializers.ChoiceField(choices=[
        ('generate customized recipe', 'Generate a recipe for me at my request'), 
        ('generate innovative recipe', 'Generate a recipe for me based on supplied ingredients'),
        ('regenerate customized recipe', 'Regenerate a new and different recipe for me based on my previous preferences'),
        ('regenerate innovative recipe', 'Regenerate a new and different recipe for me based on my previous ingredients'),
    ], required=True)
    # prompt = serializers.CharField(max_length=1024, required=True)
    max_tokens = serializers.IntegerField(min_value=1, max_value=2048, required=False, default=700)
    body_info = serializers.JSONField(required=False, default=dict)
    current_plan = serializers.JSONField(required=False, default=dict)
    user_preferences = UserPreferencesSerializer(required=False, default=dict)
    ingredients = serializers.CharField(required=False, default="")