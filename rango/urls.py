from django.urls import path
from . import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('discover/', views.discover, name='discover'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('logout/', views.logout_view, name='logout'),
]