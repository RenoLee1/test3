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
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.helpfunc import get_user_from_token
import openai
import json
from core import settings
openai.api_key = settings.OPENAI_API_KEY
import re
# from django.contrib.auth import authenticate



from rest_framework.permissions import IsAuthenticated

from .serializers import LoginSerializer



class CustomRefreshToken(RefreshToken):

    def __init__(self, *args, **kwargs):
        self.userinfo = kwargs.pop('userinfo', None)
        super().__init__(*args, **kwargs)

    @classmethod
    def for_userinfo(cls, userinfo):
        return cls(userinfo=userinfo)

    @property
    def access_token(self):
        token = super().access_token
        if self.userinfo:
            token['user_name'] = self.userinfo.user_name
            token['email'] = self.userinfo.email
            token['user_id'] = self.userinfo.id
        return token



class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = models.UserInfo.objects.all()
    serializer_class = serializers.UserInfoSerializer



class BodyInfoViewSet(viewsets.ModelViewSet):
    queryset = models.BodyInfo.objects.all()
    serializer_class = serializers.BodyInfoSerializer
    # # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    authentication_classes = []
    permission_classes = []


    @action(detail=False, methods=['POST'])
    def update_body_info(self, request, *args, **kwargs):
        # # 1. 从请求头中提取JWT Token
        # header = self.request.headers.get('Authorization')
        # if header is None:
        #     return Response({"error": "No Authorization header provided"}, status=status.HTTP_400_BAD_REQUEST)

        # # 2. 解码Token以提取用户ID
        # token = header.split(' ')[1]
        # try:
        #     untyped_token = UntypedToken(token)
        #     user_id = untyped_token["user_id"]
        #     print("User ID:", user_id)
        # except (InvalidToken, TokenError, KeyError):
        #     return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


        # # # 测试数据库
        # # all_users = models.UserInfo.objects.all()
        # # for user in all_users:
        # #     print("ID:", user.id, "User Name:", user.user_name)
        
        
        
        # # 3. 使用user_id查询你的UserInfo模型
        # try:
        #     user_info = models.UserInfo.objects.get(id=user_id)

        # except models.UserInfo.DoesNotExist:
        #     return Response({"error": "User not found233"}, status=status.HTTP_400_BAD_REQUEST)
        user_info = get_user_from_token(request)
        # 4. 根据当前用户对象获取或创建BodyInfo对象
        body_info, created = models.BodyInfo.objects.get_or_create(user=user_info)

        # 更新BodyInfo对象的字段
        serializer = self.get_serializer(body_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # 给出具体的响应，表明是创建还是更新
            if created:
                message = "BodyInfo created successfully"
            else:
                message = "BodyInfo updated successfully"
            return Response({"message": message, "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    '''get user's bodyinfo'''
    @action(detail=False, methods=['GET'])
    def get_my_body_info(self, request, *args, **kwargs):
        # 从 request.user 获取当前用户的 ID
        user_info = get_user_from_token(request)

        if user_info is None:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前用户的所有 BodyInfo 记录
        body_infos = models.BodyInfo.objects.filter(user=user_info)
        
        serializer = serializers.BodyInfoSerializer(body_infos, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    '''get bodyinfo history'''
    @action(detail=False, methods=['GET'])
    def get_body_info_history(self, request, *args, **kwargs):
        # 从 request.user 获取当前用户的 ID
        user_info = get_user_from_token(request)
        if user_info is None:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取当前用户的所有 BodyInfo 记录
        body_info = models.BodyInfo.objects.filter(user=user_info).first()
        if body_info is None:
            return Response({"error": "BodyInfo not found"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取用户的所有 BodyInfoHistory 记录并按时间排序
        body_info_histories = models.BodyInfoHistory.objects.filter(body_info=body_info).order_by('timestamp')

        serializer = serializers.BodyInfoHistorySerializer(body_info_histories, many=True)

        # 返回序列化后的数据
        return Response(serializer.data, status=status.HTTP_200_OK)





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
                user = user_query.first()
                refresh = CustomRefreshToken.for_userinfo(userinfo=user)
                token = str(refresh.access_token)
                # 登陆成功
                return Response({"message": "Login successful", "token": token}, status=status.HTTP_200_OK)
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

            # 创建JWT令牌
            refresh = CustomRefreshToken.for_user(user)
            token = str(refresh.access_token)

            return Response({"message": "Password updated successfully", "token": token}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class LogoutAPIView(APIView):
    '''注销账户'''
    
    def post(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)



class RecipesViewSet(viewsets.ModelViewSet):
    queryset = models.Recipes.objects.all()
    serializer_class = serializers.RecipesSerializer
    authentication_classes = []
    permission_classes = []
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # 如果是多个recipe的数组
            serializer = self.get_serializer(data=request.data, many=True)
        else:  # 单个recipe的情况
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        response_data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):
        created_recipes = []
        skipped_recipes = []

        # 尝试获取当前的用户，如果出错，则设置为 None
        try:
            current_user = get_user_from_token(self.request)
        except ValueError:
            current_user = None

        # 判断是否是多个数据
        is_many = isinstance(serializer.validated_data, list)

        # 如果是多个数据，则循环检查每一个
        if is_many:
            for recipe_data in serializer.validated_data:
                recipe_name = recipe_data.get('name')
                
                # 使用 get_or_create 并加入用户的判断
                recipe, created = models.Recipes.objects.get_or_create(
                    name=recipe_name,
                    user=current_user,
                    defaults={**recipe_data}
                )
                if created:
                    created_recipes.append(recipe_name)
                else:
                    skipped_recipes.append(recipe_name)
                    
        else:  # 如果是单个数据
            recipe_data = serializer.validated_data
            recipe_name = recipe_data.get('name')
            
            # 使用 get_or_create 并加入用户的判断
            recipe, created = models.Recipes.objects.get_or_create(
                name=recipe_name,
                user=current_user,
                defaults={**recipe_data}
            )
            if created:
                created_recipes.append(recipe_name)
            else:
                skipped_recipes.append(recipe_name)

        # 将创建和跳过的食谱记录到响应数据中
        response_data = {
            'created_recipes': created_recipes,
            'skipped_recipes': skipped_recipes,
        }
        return response_data
    

    @action(detail=False, methods=['post'], url_path='add_recipe')
    def add_recipe(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @action(detail=False, methods=['GET'])
    def get_my_recipes(self, request, *args, **kwargs):
        user_info = get_user_from_token(request)

        if user_info is None:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        recipes = models.Recipes.objects.filter(user=user_info)
        serializer = serializers.RecipesSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='delete_recipe')
    def delete_recipe(self, request, *args, **kwargs):
        # 获取食谱名称
        recipe_name = request.data.get('name')
        if not recipe_name:
            return Response({"error": "Recipe name not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 尝试从token中获取用户信息
        try:
            user_info = get_user_from_token(request)
        except ValueError:
            return Response({"error": "Invalid token or user not found."}, status=status.HTTP_400_BAD_REQUEST)

        # 查找食谱
        recipe = models.Recipes.objects.filter(name=recipe_name, user=user_info).first()
        if not recipe:
            return Response({"error": "Recipe not found for the specified user."}, status=status.HTTP_404_NOT_FOUND)

        # 删除食谱
        recipe.delete()

        return Response({"message": "Recipe deleted successfully."}, status=status.HTTP_200_OK)



class DailyMealPlanViewSet(viewsets.ModelViewSet):
    queryset = models.DailyMealPlan.objects.all()
    serializer_class = serializers.DailyMealPlanSerializer
    authentication_classes = []
    permission_classes = []

    # @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated] )
    @action(detail=True, methods=['post'])
    def modify_meal(self, request, pk=None):
        meal_time = request.data.get('meal_time')
        recipe_ids = request.data.get('recipe_ids', [])
        action_type = request.data.get('action_type', 'set')

        daily_meal_plan = self.get_object()

        if daily_meal_plan.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if meal_time not in ['breakfast', 'lunch', 'dinner']:
            return Response({'error': 'Invalid meal_time'}, status=status.HTTP_400_BAD_REQUEST)

        if action_type not in ['add', 'remove', 'set']:
            return Response({'error': 'Invalid action_type'}, status=status.HTTP_400_BAD_REQUEST)

        meal_queryset = getattr(daily_meal_plan, meal_time)

        recipes = models.Recipes.objects.filter(pk__in=recipe_ids)
        if len(recipes) != len(recipe_ids):
            return Response({'error': 'One or more recipes not found'}, status=status.HTTP_404_NOT_FOUND)

        if action_type == 'set':
            meal_queryset.clear()
            meal_queryset.set(recipes)
        elif action_type == 'add':
            meal_queryset.add(*recipes)
        elif action_type == 'remove':
            meal_queryset.remove(*recipes)

        return Response({'message': 'Meal modified successfully'}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'])
    def get_my_daily_meal_plans(self, request, *args, **kwargs):
        user_info = get_user_from_token(request)

        if user_info is None:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        daily_meal_plans = models.DailyMealPlan.objects.filter(user=user_info)
        serializer = serializers.DailyMealPlanSerializer(daily_meal_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

# 修改自定义计划时要先从计划中获取对应的每日计划的id，然后找到那个每日计划再修改。
class CustomMealPlanViewSet(viewsets.ModelViewSet):
    queryset = models.CustomMealPlan.objects.all()
    serializer_class = serializers.CustomMealPlanSerializer
    authentication_classes = []
    permission_classes = []

    # @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @action(detail=True, methods=['post'])
    def update_daily_meal(self, request, pk=None):
        custom_meal_plan = self.get_object()

        # 检查该计划是否属于当前用户
        if custom_meal_plan.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        daily_meal_plan_id = request.data.get('daily_meal_plan_id')
        try:
            daily_meal_plan = models.DailyMealPlan.objects.get(pk=daily_meal_plan_id)
        except models.DailyMealPlan.DoesNotExist:
            return Response({'error': 'Daily meal plan not found'}, status=status.HTTP_404_NOT_FOUND)

        # 添加或更新daily_meal_plan
        custom_meal_plan.daily_plans.add(daily_meal_plan)
        custom_meal_plan.save()  # 保存更改
        return Response({'message': 'Daily meal plan updated successfully'}, status=status.HTTP_200_OK)


    # @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @action(detail=True, methods=['post'])
    def remove_daily_meal(self, request, pk=None):
        custom_meal_plan = self.get_object()

        # 检查该计划是否属于当前用户
        if custom_meal_plan.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        daily_meal_plan_id = request.data.get('daily_meal_plan_id')
        try:
            daily_meal_plan = models.DailyMealPlan.objects.get(pk=daily_meal_plan_id)
        except models.DailyMealPlan.DoesNotExist:
            return Response({'error': 'Daily meal plan not found'}, status=status.HTTP_404_NOT_FOUND)

        # 从custom_meal_plan中移除daily_meal_plan
        custom_meal_plan.daily_plans.remove(daily_meal_plan)
        custom_meal_plan.save()  # 保存更改
        return Response({'message': 'Daily meal plan removed successfully'}, status=status.HTTP_200_OK)
        
        
    @action(detail=False, methods=['GET'])
    def get_my_custom_meal_plans(self, request, *args, **kwargs):
        user_info = get_user_from_token(request)

        if user_info is None:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        custom_meal_plans = models.CustomMealPlan.objects.filter(user=user_info)
        serializer = serializers.CustomMealPlanSerializer(custom_meal_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            

class GenerateRecipeView(APIView):

    # 这是您定义的选择项，用于后续的查找
    REQUEST_TYPE_CHOICES = {
        'generate customized recipe': 'Generate a recipe for me at my request',
        'generate innovative recipe': 'Generate a recipe for me based on supplied ingredients'
    }


    def post(self, request, *args, **kwargs):
        serializer = serializers.GPTRecipeAdviceSerializer(data=request.data)
        sample_recipe = {
            "id": 1,
            "name": "香煎三文鱼",
            "calories": "300",
            "fat": "15.50",
            "protein": "30.00",
            "carbohydrate": "10.00",
            "introduction": "香煎三文鱼是一道简单而美味的菜肴。首先,将三文鱼块用盐和胡椒调味,然后在热锅中用橄榄油煎至金黄色,大约每面煎2-3分钟。最后,撒上一些新鲜的柠檬汁,即可享用。"
        }
        if serializer.is_valid():
            data = serializer.validated_data
            user_prefs_data = data.get('user_preferences', {})

            # 从token中提取用户信息
            try:
                user_info = get_user_from_token(request)
            except ValueError as e:
                # 如果从Token中无法提取有效的UserInfo，返回400 Bad Request
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # 查询或创建用户偏好
            user_prefs, created = models.UserPreferences.objects.get_or_create(user=user_info)
            
            # 如果提供了用户偏好，更新它们
            if 'dietary_requirements' in user_prefs_data:
                user_prefs.dietary_requirements = user_prefs_data['dietary_requirements']
            if 'fitness_goal' in user_prefs_data:
                user_prefs.fitness_goal = user_prefs_data['fitness_goal']
            if 'taste_preference' in user_prefs_data:
                user_prefs.taste_preference = user_prefs_data['taste_preference']

            # 保存用户的偏好
            user_prefs.save()

            # 构建prompt
            prompt = 'please use english:' + self.REQUEST_TYPE_CHOICES.get(data['request_type'])

            # 如果是自定义食谱请求，则添加用户的偏好到提示中

            if data['request_type'] == 'generate customized recipe':
                '''根据喜好生成食谱'''
                
                
                # 添加用户的偏好到提示语句中，只在有值时添加
                if user_prefs.dietary_requirements:
                    prompt += f"\nDietary Requirements: {user_prefs.dietary_requirements}"
                if user_prefs.fitness_goal:
                    prompt += f"\nFitness Goal: {user_prefs.fitness_goal}"
                if user_prefs.taste_preference:
                    prompt += f"\nTaste Preferences: {user_prefs.taste_preference}"
                prompt += "\nPlease generate a new recipe for me based on the preferences provided, in the format specified below.Make sure calories, fat, protein, and carbohydrate have a fixed value of two decimal places. The output must be in json form:\n"
                prompt += json.dumps(sample_recipe, ensure_ascii=False)
            
            elif data['request_type'] == 'generate innovative recipe':
                '''根据食材生成食谱'''
                
                
                ingredients_string = data.get('ingredients', '')
                # 将选择的食材保存到 last_ingredients 字段中
                last_ingredients_obj, created = models.Last_ingredients.objects.get_or_create(user=user_info)
                last_ingredients_obj.last_ingredients = ingredients_string
                last_ingredients_obj.save()

                ingredients_list = [item.strip() for item in re.split(r'[，、。\s]+', ingredients_string) if item]
                if not ingredients_list:
                    return Response({"error": "请提供食材列表"}, status=status.HTTP_400_BAD_REQUEST)
                
                # 将要求输入prompt
                prompt = "Generate recipes based on the following ingredients:\n" + ', '.join(ingredients_list)
                prompt += "\nPlease generate a new recipe for me based on the ingredients provided in the format specified below. Make sure calories, fat, protein, and carbohydrate have a fixed value of two decimal places. The output must be in json form:\n"
                prompt += json.dumps(sample_recipe, ensure_ascii=False)
            # 使用OpenAI API
            # 最大尝试次数
            MAX_RETRIES = 5

            # 获取当前用户的所有食谱的名字
            existing_recipes_names = models.Recipes.objects.filter(user=user_info).values_list('name', flat=True)

            for _ in range(MAX_RETRIES):
                try:
                    # 使用OpenAI API来重新生成食谱
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=700
                    )
                    parsed_response = json.loads(response.get("choices")[0]["message"]["content"])

                    # 检查这是否与该用户的任何先前的食谱重复
                    if parsed_response["name"] not in existing_recipes_names:
                        # 如果食谱是独特的，跳出循环
                        break

                except json.JSONDecodeError:
                    # 如果解析失败，继续循环尝试
                    continue
                except Exception as e:
                    # 其他错误
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                # 如果尝试多次后仍然失败
                return Response({"error": "无法生成唯一的食谱，请稍后再试。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 返回生成的食谱
            return Response({"response": parsed_response})

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



'''再次生成'''
class RegenerateRecipeView(APIView):

    def post(self, request, *args, **kwargs):
        sample_recipe = {
            "id": 1,
            "name": "香煎三文鱼",
            "calories": "300",
            "fat": "15.50",
            "protein": "30.00",
            "carbohydrate": "10.00",
            "introduction": "香煎三文鱼是一道简单而美味的菜肴。首先,将三文鱼块用盐和胡椒调味,然后在热锅中用橄榄油煎至金黄色,大约每面煎2-3分钟。最后,撒上一些新鲜的柠檬汁,即可享用。"
        }
        prompt = "please use english"
        serializer = serializers.GPTRecipeAdviceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        request_type = serializer.validated_data['request_type']

        try:
            # 获取当前用户
            user_info = get_user_from_token(request)
        except ValueError as e:
            if str(e) == "No Authorization header provided":
                return Response({"error": "你需要登录"}, status=status.HTTP_401_UNAUTHORIZED)
            elif str(e) == "Token无效":
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif str(e) == "用户未找到":
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Unknown error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if "regenerate" in request_type:
            if request_type == "regenerate customized recipe":
        
                # 获取用户的偏好
                try:
                    user_prefs = models.UserPreferences.objects.get(user=user_info)
                except models.UserPreferences.DoesNotExist:
                    return Response({"error": "用户偏好设置未找到"}, status=status.HTTP_404_NOT_FOUND)

                
                dietary_req = user_prefs.dietary_requirements
                fitness_goal = user_prefs.fitness_goal
                taste_pref = user_prefs.taste_preference

                # 构建prompt
                prompt += "Regenerate a new and different recipe for me at my request"
                if dietary_req:
                    prompt += f"\nDietary Requirements: {dietary_req}"
                if fitness_goal:
                    prompt += f"\nFitness Goal: {fitness_goal}"
                if taste_pref:
                    prompt += f"\nTaste Preferences: {taste_pref}"
                prompt += "\nPlease generate a new recipe for me based on the preferences provided, in the format specified below.Make sure calories, fat, protein, and carbohydrate have a fixed value of two decimal places. The output must be in json form:\n"
                
                prompt += json.dumps(sample_recipe, ensure_ascii=False)
            
            elif request_type == "regenerate innovative recipe":
                # 使用上次的食材重新生成食谱
                try:
                    last_ingredients_instance = models.Last_ingredients.objects.get(user=user_info)
                    last_ingr = last_ingredients_instance.last_ingredients
                except models.Last_ingredients.DoesNotExist:
                    return Response({"error": "上一次的食材记录未找到"}, status=status.HTTP_400_BAD_REQUEST)
                ingredients_list = [item.strip() for item in re.split(r'[，、。\s]+', last_ingr) if item]
                if not ingredients_list:
                    return Response({"error": "上一次的食材列表为空"}, status=status.HTTP_400_BAD_REQUEST)
                
                prompt += "Create a new and different recipe based on the following ingredients:\n" + ', '.join(ingredients_list)
                prompt += "\nPlease generate a new recipe for me based on the ingredients provided in the format specified below. Make sure calories, fat, protein, and carbohydrate have a fixed value of two decimal places. The output must be in json form:\n"
                prompt += json.dumps(sample_recipe, ensure_ascii=False)

            else:
                return Response({"error": "无效的request_type"}, status=status.HTTP_400_BAD_REQUEST)

        # 使用OpenAI API来重新生成食谱
        # try:
        #     response = openai.ChatCompletion.create(
        #         model="gpt-3.5-turbo",
        #         messages=[{"role": "user", "content": prompt}],
        #         # prompt=prompt,
        #         max_tokens=700  
        #     )
        #     # parsed_response = json.loads(response.get("choices")[0]["message"]["content"])
        #     try:
        #         parsed_response = json.loads(response.get("choices")[0]["message"]["content"])
        #     except json.JSONDecodeError:
        #         print("Failed to parse JSON. Raw GPT output:", response.get("choices")[0]["message"]["content"])
        #         return Response({"error": "Failed to parse recipe generated by GPT"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #     return Response({"response": parsed_response})
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        # 最大尝试次数
        MAX_RETRIES = 5

        # 获取当前用户的所有食谱的名字
        existing_recipes_names = models.Recipes.objects.filter(user=user_info).values_list('name', flat=True)

        for _ in range(MAX_RETRIES):
            try:
                # 使用OpenAI API来重新生成食谱
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700
                )
                parsed_response = json.loads(response.get("choices")[0]["message"]["content"])

                # 检查这是否与该用户的任何先前的食谱重复
                if parsed_response["name"] not in existing_recipes_names:
                    # 如果食谱是独特的，则退出循环
                    break
                
            except json.JSONDecodeError:
                # 如果解析失败，继续循环尝试
                continue
            except Exception as e:
                # 其他错误
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            # 如果尝试多次后仍然失败
            return Response({"error": "无法生成唯一的食谱，请稍后再试。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({"response": parsed_response})
