from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from meal import models
from . import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.encrypt import md5
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from .serializers import LoginSerializer


class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = models.UserInfo.objects.all()
    serializer_class = serializers.UserInfoSerializer


class BodyInfoViewSet(viewsets.ModelViewSet):
    queryset = models.BodyInfo.objects.all()
    serializer_class = serializers.BodyInfoSerializer

    @action(detail=False, methods=['POST'])
    def update_body_info(self, request, *args, **kwargs):
        # 获取当前session中的用户信息
        user_info = request.session.get('info')

        # 确保用户信息在session中存在
        if not user_info:
            return Response({'error': 'You must be logged in to update body info'}, status=status.HTTP_404_NOT_FOUND)

        # 获取 user_id 并检查其有效性
        user_id = user_info.get('id')
        if not user_id:
            return Response({'error': 'User ID not found in session'}, status=status.HTTP_400_BAD_REQUEST)

        # 根据session中的user ID获取或创建BodyInfo对象
        body_info, created = models.BodyInfo.objects.get_or_create(user=models.UserInfo.objects.get(id=user_id))

        # 更新BodyInfo对象的字段
        serializer = self.get_serializer(body_info, data=request.data, partial=True)
        if serializer.is_valid():
            body_info.user = models.UserInfo.objects.get(id=user_id)
            serializer.save()

            # 给出具体的响应，表明是创建还是更新
            if created:
                message = "BodyInfo created successfully"
            else:
                message = "BodyInfo updated successfully"
            return Response({"message": message, "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = models.Recipes.objects.all()
    serializer_class = serializers.RecipesSerializer


class RegisterView(CreateAPIView):
    '''注册'''

    serializer_class = serializers.RegisterSerializer


class LoginAPIView(APIView):
    '''登录'''

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user_name = serializer.validated_data['user_name']
            password = serializer.validated_data['password']

            hashed_password = md5(password)

            user_query = models.UserInfo.objects.filter(user_name=user_name, password=hashed_password)
            user_exists = user_query.exists()

            if user_exists:
                user_object = user_query.first()
                request.session['info'] = {'id': user_object.id, 'name': user_object.user_name}
                # 登陆成功
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                # 登录失败
                return Response({"error": "The account or password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordAPIView(APIView):
    '''忘记密码/重置密码/修改密码'''

    def post(self, request, *args, **kwargs):
        serializer = serializers.ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # 获取验证后的数据
            validated_data = serializer.validated_data

            # 不存在则返回404错误
            user = get_object_or_404(
                models.UserInfo,
                user_name=validated_data['user_name'],
                email=validated_data['email']
            )

            # 更新密码
            user.password = md5(validated_data['password'])
            user.save()

            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    '''注销账户'''

    def post(self, request):
        request.session.clear()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


'''添加食谱至一天的计划当中'''


@action(detail=True, methods=['post'])
def add_recipe_to_meal(self, request, pk=None):
    # 获取要添加的菜谱ID和餐时
    recipe_id = request.data.get('recipe_id')
    meal_time = request.data.get('meal_time')  # 三选一：'breakfast', 'lunch' 或 'dinner'

    # 获取用户的日常餐饮计划
    daily_meal_plan = self.get_object()

    # 检查要添加的菜谱是否存在
    if not models.Recipes.objects.filter(pk=recipe_id).exists():
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    # 获取要添加的菜谱
    recipe = models.Recipes.objects.get(pk=recipe_id)

    # 将菜谱添加到相应的餐时
    if meal_time == 'breakfast':
        daily_meal_plan.breakfast.add(recipe)
    elif meal_time == 'lunch':
        daily_meal_plan.lunch.add(recipe)
    elif meal_time == 'dinner':
        daily_meal_plan.dinner.add(recipe)

    return Response({'message': 'Recipe added to meal successfully'}, status=status.HTTP_201_CREATED)