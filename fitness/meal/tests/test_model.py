from django.test import TestCase
from meal.models import UserInfo, BodyInfo

class TestModels(TestCase):
    def setUp(self):
        self.user = UserInfo.objects.create(
            user_name='reno',
            email='123@gmail.com',
            password='123'
        )

    def test_get_name(self):
        self.assertEquals(self.user.user_name, 'reno')

    def test_security_code(self):
        self.assertEquals(self.user.password, '123')