from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import path
# Create your views here.
app_name = 'meal'

urlpatterns = [
    path('', TemplateView.as_view(template_name="meal/index.html"))
]