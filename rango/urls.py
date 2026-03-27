from django.urls import path
from . import views
app_name = 'rango'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('discover/', views.discover, name='discover'),
    path('profile/', views.profile, name='profile'),
    path('movie/<str:media_type>/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    path('add_favourite/<int:movie_id>/', views.add_favourite, name='add_favourite'),
    path('movie/<str:media_type>/<int:tmdb_id>/save/', views.save_review_rating, name='save_review_rating'),
]