from django.urls import path
from . import views
<<<<<<< HEAD
app_name='rango'
urlpatterns=[
    path('',views.index,name='index'),
    path('home/',views.home,name='home'),
    path('register/',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('discover/',views.discover,name='discover'),
    path('profile/',views.profile,name='profile'),
    path('movie/<str:media_type>/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    path('add_favourite/<int:movie_id>/',views.add_favourite,name='add_favourite'
),
=======

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
    path('add_favourite/<int:movie_id>/', views.add_favourite, name='add_favourite'),
>>>>>>> 50abc892e6df2d27db9cf04beecc553cb486bf81
]