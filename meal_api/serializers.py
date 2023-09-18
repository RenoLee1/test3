from rest_framework import serializers
from meal import models
from utils.encrypt import md5


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'email', 'password']


class BodyInfoSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.BodyInfo
        fields = ['height', 'weight', 'age', 'gender', 'user']


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipes
        fields = ['name', 'calories', 'fat', 'introduction']


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


class DailyMealPlanSerializer(serializers.ModelSerializer):
    breakfast = RecipesSerializer(many=True, read_only=True)
    lunch = RecipesSerializer(many=True, read_only=True)
    dinner = RecipesSerializer(many=True, read_only=True)

    class Meta:
        model = models.DailyMealPlan
        fields = ('id', 'user', 'breakfast', 'lunch', 'dinner', 'date')


'''OpenAI'''


class GPT3RecipeAdviceSerializer(serializers.Serializer):
    request_type = serializers.ChoiceField(
        choices=[('improve_current', 'Improve Current Recipe'), ('new_recipe', 'Generate New Recipe')], required=True)
    prompt = serializers.CharField(max_length=1024, required=True)
    max_tokens = serializers.IntegerField(min_value=1, max_value=2048, required=False, default=150)
    body_info = serializers.JSONField(required=False, default=dict)
    current_plan = serializers.JSONField(required=False, default=dict)