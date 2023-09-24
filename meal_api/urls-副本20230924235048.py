from rest_framework import routers
from . import views
from django.urls import path, include


app_name='meal_api'

router = routers.DefaultRouter()
router.register(r'userinfo', views.UserInfoViewSet)
router.register(r'bodyinfo', views.BodyInfoViewSet, basename='bodyinfo')
router.register(r'recipe', views.RecipesViewSet, basename='recipe')
router.register(r'daily_meal_plans', views.DailyMealPlanViewSet)
router.register(r'custom_meal_plans', views.CustomMealPlanViewSet)



urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('forget_password/', views.ForgetPasswordAPIView.as_view(), name='forget_password'),
    path('bodyinfo/update/', views.BodyInfoViewSet.as_view({'post': 'update_body_info'}), name='update-body-info'),
    path('', include(router.urls)),
    path('generate_recipe/', views.GenerateRecipeView.as_view(), name='generate_recipe'),
    path('regenerate_recipe/', views.RegenerateRecipeView.as_view(), name='regenerate_recipe'),
]