from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('forget_pwd/', views.forget_pwd, name='forget_pwd'),
    path('fit/', views.fit, name='fit'),
    # path('test/',views.chat_box)
]