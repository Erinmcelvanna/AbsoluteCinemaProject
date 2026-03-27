from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import UserProfile, Movie, Favourite, WatchHistory


def index(request):
    return render(request, 'rango/index.html')


def home(request):
    movies = Movie.objects.all()[:5]
    return render(request, 'rango/home.html', {'movies': movies})


def register_view(request):
    context = {}

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email or not username or not password1 or not password2:
            context['error'] = 'Please fill in all fields.'
        elif password1 != password2:
            context['error'] = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('rango:profile')

    return render(request, 'rango/register.html', context)


def login_view(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('rango:profile')
        else:
            context['error'] = 'Invalid username or password.'

    return render(request, 'rango/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('rango:index')


def discover(request):
    query = request.GET.get('q', '').strip()

    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = Movie.objects.all()

    context = {
        'movies': movies
    }

    return render(request, 'rango/discover.html', context)


@login_required
def profile(request):
    favourite_movies = Movie.objects.filter(
        favourited_by__user=request.user
    ).distinct()

    recently_watched = Movie.objects.filter(
        watch_histories__user=request.user
    ).distinct()

    context = {
        'favourite_movies': favourite_movies,
        'recently_watched': recently_watched,
    }

    return render(request, 'rango/profile.html', context)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    context = {'movie': movie}
    return render(request, 'rango/movieDetail.html', context)


@login_required
def add_favourite(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=movie_id)

        Favourite.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"})