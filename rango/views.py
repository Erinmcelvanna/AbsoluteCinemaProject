from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

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

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('rango:profile')

    return render(request, 'rango/register.html', context)


def login_view(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('rango:profile')
        else:
            context['error'] = 'Invalid username or password.'

    return render(request, 'rango/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('rango:index')


def discover(request):
    query = request.GET.get('q', '').strip()
    selected_type = request.GET.get('type', 'all').lower()

    movies = Movie.objects.all()

    if query:
        search_query = Q(title__icontains=query)

        movie_field_names = [field.name for field in Movie._meta.fields]

        if 'genre' in movie_field_names:
            search_query |= Q(genre__icontains=query)
        if 'director' in movie_field_names:
            search_query |= Q(director__icontains=query)
        if 'actor' in movie_field_names:
            search_query |= Q(actor__icontains=query)
        if 'actors' in movie_field_names:
            search_query |= Q(actors__icontains=query)
        if 'description' in movie_field_names:
            search_query |= Q(description__icontains=query)

        movies = movies.filter(search_query)

    movie_field_names = [field.name for field in Movie._meta.fields]

    if selected_type == 'films':
        if 'content_type' in movie_field_names:
            movies = movies.filter(content_type__iexact='film')
        elif 'category' in movie_field_names:
            movies = movies.filter(category__iexact='film')
        elif 'type' in movie_field_names:
            movies = movies.filter(type__iexact='film')
        elif 'is_series' in movie_field_names:
            movies = movies.filter(is_series=False)

    elif selected_type == 'series':
        if 'content_type' in movie_field_names:
            movies = movies.filter(content_type__iexact='series')
        elif 'category' in movie_field_names:
            movies = movies.filter(category__iexact='series')
        elif 'type' in movie_field_names:
            movies = movies.filter(type__iexact='series')
        elif 'is_series' in movie_field_names:
            movies = movies.filter(is_series=True)

    context = {
        'movies': movies,
        'query': query,
        'selected_type': selected_type,
    }

    return render(request, 'rango/discover.html', context)


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    favourite_movies = Movie.objects.filter(
        favourited_by__user=request.user
    ).distinct()

    recently_watched = Movie.objects.filter(
        watch_histories__user=request.user
    ).distinct()

    context = {
        'user_profile': user_profile,
        'username': request.user.username,
        'email': request.user.email,
        'favourite_movies': favourite_movies,
        'recently_watched': recently_watched,
        'favourite_count': favourite_movies.count(),
        'watched_count': recently_watched.count(),
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

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'})