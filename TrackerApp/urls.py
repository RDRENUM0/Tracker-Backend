from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'daily-entries', views.DailyEntryViewSet, basename='daily-entries')

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.get_user_profile, name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Daily entries endpoints
    path('', include(router.urls)),
]