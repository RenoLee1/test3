from django.test import SimpleTestCase
from django.urls import reverse, resolve
from meal.views import login, register, forget_pwd, fit

class TestUrls(SimpleTestCase):
    def test_login_url(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login)

    def test_register_url(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, register)

    def test_forget_pwd_url(self):
        url = reverse('forget_pwd')
        self.assertEquals(resolve(url).func, forget_pwd)

    def test_fit_url(self):
        url = reverse('fit')
        self.assertEquals(resolve(url).func, fit)


