import json

from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from meal.models import UserInfo, BodyInfo, Recipes
from utils.encrypt import md5
from django.contrib.auth.models import User
# Create your tests here.
class PostTests(APITestCase):

    def setUp(self):
        # 创建一个测试用户
        self.user = UserInfo.objects.create(
            user_name="reno1",
            email="a@a.com",
            password=md5("123456")
        )

        # 创建一个 API 客户端
        self.client = APIClient()

    def test_view_userinfo(self):

        # 测试register
        reg_url = reverse('meal_api:register')

        data = {
            "user_name": "reno",
            "password": "123",
            "confirm_password": "123",
            "email": "d@d.com"
        }

        reg_response = self.client.post(reg_url, data, follow='json')
        self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

        # 测试login
        login_url = reverse('meal_api:login')
        data1 = {
            "user_name": "reno",
            "password": "123"
        }

        login_response = self.client.post(login_url, data1, follow='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # 测试 forget_password
        forget_url = reverse('meal_api:forget_password')
        data_forget = {
            "user_name": "reno",
            "password": "1234",
            "confirm_password": "1234",
            "email": "d@d.com"
        }

        response_forget = self.client.post(forget_url, data_forget, follow='json')
        self.assertEqual(response_forget.status_code, status.HTTP_200_OK)

    def test_recipes(self):
        # 测试recipe
        recipes_url = reverse('meal_api:recipe-list')

        # 测试get请求
        recipe_get_response = self.client.get(recipes_url, follow='json')
        self.assertEqual(recipe_get_response.status_code, status.HTTP_200_OK)

        # 测试post请求
        recipes_post_url = reverse('meal_api:recipe-list')
        recipes_data = {
            "name": "EggTomato",
            "calories": "254KJ",
            "fat": "54g",
            "introduction": "This is my first recipe"
        }

        recipes_response = self.client.post(recipes_post_url, recipes_data, follow='json')
        created_recipe = Recipes.objects.get(id=1)

        # 检测是否存储成功
        self.assertEqual(str(created_recipe), 'EggTomato')
        self.assertEqual(recipes_response.status_code, status.HTTP_201_CREATED)

    def test_body_info(self):
        # 模拟登陆
        login_url = reverse('meal_api:login')
        data1 = {
            "user_name": "reno1",
            "password": "123456"
        }

        login_response = self.client.post(login_url, data1, follow='json')

        # 创建body
        data = {
            "height": "180cm",
            "weight": "75kg",
            "age": 30,
            "gender": 2,
        }

        body_info_url = reverse('meal_api:update-body-info')
        response = self.client.post(body_info_url, data, follow='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_body_info = BodyInfo.objects.get(id=1)

        self.assertTrue(updated_body_info.user)
        self.assertTrue(updated_body_info)
        self.assertEqual(updated_body_info.height, "180cm")
        self.assertEqual(updated_body_info.weight, "75kg")

        # 测试更改bodyInfo
        data = {
            "height": "190cm",
            "weight": "70kg",
            "age": 50,
            "gender": 1,
        }

        body_info_change_url = reverse('meal_api:update-body-info')
        chnage_response = self.client.post(body_info_change_url, data, follow='json')

        self.assertEqual(chnage_response.status_code, status.HTTP_200_OK)

        updated_body_info = BodyInfo.objects.get(id=1)
        self.assertTrue(updated_body_info.user)
        self.assertTrue(updated_body_info)
        self.assertEqual(updated_body_info.height, "190cm")
        self.assertEqual(updated_body_info.weight, "70kg")

    def test_log_out(self):
        # 模拟登陆
        login_url = reverse('meal_api:login')
        data1 = {
            "user_name": "reno1",
            "password": "123456"
        }

        login_response = self.client.post(login_url, data1, follow='json')

        log_out_url = reverse('meal_api:logout')
        log_out_response = self.client.post(log_out_url)

        self.assertEqual(log_out_response.status_code, status.HTTP_200_OK)






















