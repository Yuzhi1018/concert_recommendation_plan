"""
URL configuration for concert_plan_recommender project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from recommend_plan.views import signup_view
from recommend_plan.views import weights_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recommend_plan.urls')),
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='recommend_plan/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('weights/', weights_view, name='weights')
]
