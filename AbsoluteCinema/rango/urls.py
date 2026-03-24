from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    path('movies/', views.movies, name='movies'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),

    path('movies/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('movies/<int:movie_id>/reviews/', views.movie_reviews, name='movie_reviews'),

    path('ranked/', views.ranked, name='ranked'),

    path('profile/', views.profile, name='profile'),
    path('profile/favourites/', views.favourites, name='favourites'),
    path('profile/add_favourite/<int:movie_id>/', views.add_favourite, name='add_favourite'),
    path('profile/remove_favourite/<int:movie_id>/', views.remove_favourite, name='remove_favourite'),

    path('profile/watch-history/', views.watch_history, name='watch_history'),
    path('profile/add_watch/<int:movie_id>/', views.add_watch_history, name='add_watch_history'),
]