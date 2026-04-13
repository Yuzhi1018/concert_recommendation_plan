from django.urls import path
from . import views
from .views import search_concerts

app_name = "recommend_plan"
urlpatterns = [
    path('weights/', views.weights_view, name='weights'),
    path('', views.index, name='index'),
    path('search/', search_concerts, name='search_concerts'),
    path('openai_page/', views.openai_page, name='openai_page'),
]