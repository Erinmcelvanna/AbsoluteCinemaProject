from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
from .models import Movie, Rating, Review, WatchHistory,Favourite

TMDB_API_KEY ="f0efa2032b75218ca0109f65455e33b3"
def index(request):
    url = "https://api.themoviedb.org/3/trending/all/week"
    params = {
        "api_key": "f0efa2032b75218ca0109f65455e33b3"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print("STATUS CODE:", response.status_code, flush=True)
    print("NUMBER OF RESULTS:", len(data.get("results", [])), flush=True)
    trending_titles = data.get("results", [])

    context = {
        "trending_titles": trending_titles
    }

    return render(request, 'rango/index.html',context)

def home(request):
    api_key = "f0efa2032b75218ca0109f65455e33b3"

    # Trending
    trending = requests.get(
        "https://api.themoviedb.org/3/trending/all/week",
        params={"api_key": api_key}
    ).json().get("results", [])
    trending = [item for item in trending if item.get("media_type") in ["movie", "tv"]]
    # Popular Movies
    movies = requests.get(
        "https://api.themoviedb.org/3/movie/popular",
        params={"api_key": api_key}
    ).json().get("results", [])

    # Popular TV
    tv = requests.get(
        "https://api.themoviedb.org/3/tv/popular",
        params={"api_key": api_key}
    ).json().get("results", [])

    return render(request, "rango/home.html", {
        "trending": trending[:10],
        "movies": movies[:10],
        "tv": tv[:10],
    })

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
    media_type_filter = request.GET.get('type', '').strip()

    if query:
        url = "https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": "f0efa2032b75218ca0109f65455e33b3",
            "query": query
        }
    else:
        url = "https://api.themoviedb.org/3/trending/all/week"
        params = {
            "api_key": "f0efa2032b75218ca0109f65455e33b3"
        }

    response = requests.get(url, params=params)
    data = response.json()

    movies = data.get("results", [])
    movies = [item for item in movies if item.get("media_type") in ["movie", "tv"]]

    if media_type_filter in ["movie", "tv"]:
        movies = [item for item in movies if item.get("media_type") == media_type_filter]

    return render(request, "rango/discover.html", {
        "movies": movies,"selected_type": media_type_filter,
    })
@login_required
def profile(request):
    favourite_movies = Movie.objects.filter(
        favourited_by__user=request.user
    ).distinct()

    recently_watched = Movie.objects.filter(
        watch_histories__user=request.user
    ).distinct().order_by('-watch_histories__watched_at')
    reviews_count = Review.objects.filter(user=request.user).count()
    context = {
        'favourite_movies': favourite_movies,
        'recently_watched': recently_watched,
        'watched_count': recently_watched.count(),
        'favourites_count': favourite_movies.count(),
        'reviews_count': reviews_count,
    }

    return render(request, 'rango/profile.html', context)

@login_required
def save_review_rating(request, media_type, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    if request.method == "POST":
        rating_value = request.POST.get("rating")
        review_text = request.POST.get("content")

        if rating_value:
            Rating.objects.update_or_create(
                user=request.user,
                movie=movie,
                defaults={"score": int(rating_value)}
            )
            WatchHistory.objects.get_or_create(
                user=request.user,
                movie=movie
         )
        if review_text and review_text.strip():
            Review.objects.create(
                user=request.user,
                movie=movie,
                content=review_text.strip()
            )

    return redirect("rango:movie_detail", media_type=media_type, tmdb_id=tmdb_id)

def movie_detail(request,media_type ,tmdb_id):
    TMDB_API_KEY = "f0efa2032b75218ca0109f65455e33b3"
    if media_type == "tv":
            url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    else:
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    params = {
            "api_key":"f0efa2032b75218ca0109f65455e33b3"
        }

    response = requests.get(url, params=params)
    movie_data = response.json()

    title = movie_data.get("title") or movie_data.get("name") or "Unknown Title"
    release_date = movie_data.get("release_date") or movie_data.get("first_air_date") or ""
    year = int(release_date[:4]) if release_date and len(release_date) >= 4 else 1
    poster_path = movie_data.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    description = movie_data.get("overview", "")

    movie_obj, created = Movie.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": title,
            "media_type": media_type,
            "year": year,
            "poster": poster_url,
            "description": description,
            "cast": "",
        }
    )

    reviews = movie_obj.reviews.all()
    user_rating = None

    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(user=request.user, movie=movie_obj).first()
        if existing_rating:
            user_rating = existing_rating.score

    return render(request, "rango/movieDetail.html", {
        "movie": movie_data,
        "movie_obj": movie_obj,
        "media_type": media_type,
        "reviews": reviews,
        "user_rating": user_rating,
    })

@login_required
def add_favourite(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=movie_id)

        Favourite.objects.get_or_create(
            user=request.user,
            movie=movie
        )
        WatchHistory.objects.get_or_create(
            user=request.user,
            movie=movie
        )
        return redirect('rango:profile')

    return redirect('rango:profile')