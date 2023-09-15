from django.test import TestCase, Client
from django.urls import reverse, resolve
from meal.models import UserInfo, BodyInfo
from bs4 import BeautifulSoup

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserInfo.objects.create(
            user_name='reno',
            email='123@gmail.com',
            password='123'
        )


    def test_valid_login_GET(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_POST_valid_credentials(self):
        url = reverse('login')  # 假设您的登录视图的 URL 名称为 'login'
        data = {
            'user_name': 'reno',
            'password': '123',
            'login': 'login',  # 登录按钮的名称，根据您的视图配置来确定
        }
        response = self.client.post(url, data, follow=True)
        print(response.status_code)  # 打印状态码
        print(response.content)  # 打印响应内容

        self.assertEqual(response.status_code, 302)

    # def test_login_POST_invalid_credentials(self):
    #     url = reverse('login')  # 假设您的登录视图的 URL 名称为 'login'
    #     data = {
    #         'user_name': 'invalid_user',
    #         'password': 'invalid_password',
    #         'login': 'login',  # 登录按钮的名称，根据您的视图配置来确定
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)  # 检查 POST 请求的响应状态码，您可以根据实际情况更改此断言


    # def test_valid_login(self):
    #     url = reverse('login')
    #     data = {
    #         'user_name': 'reno',
    #         'password': '123',
    #         'login': 'login',  # 这个是登录按钮的名称，根据您的视图配置来确定
    #     }
    #     response = self.client.post(url, data)
    #
    #     # 检查登录是否成功，可以根据您的视图逻辑来修改此部分
    #     self.assertEqual(response.status_code, 200)


