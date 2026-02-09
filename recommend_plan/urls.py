from django.urls import path
from . import views

app_name = "recommend_plan"
urlpatterns = [
    path('', views.index, name='index'),
]