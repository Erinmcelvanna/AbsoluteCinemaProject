from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Movie, Rating, Review, Favourite, WatchHistory


def index(request):
    return render(request, 'index.html')


def home(request):
    movies = Movie.objects.all()[:5]
    return render(request, 'home.html', {'movies': movies})


def movies(request):
    movies = Movie.objects.all()
    return render(request, 'movies.html', {'movies': movies})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = movie.reviews.all()
    ratings = movie.ratings.all()
    average_rating = movie.average_rating()

    is_favourite = False
    has_rated = False

    if request.user.is_authenticated:
        is_favourite = Favourite.objects.filter(user=request.user, movie=movie).exists()
        has_rated = Rating.objects.filter(user=request.user, movie=movie).exists()

    context = {
        'movie': movie,
        'reviews': reviews,
        'ratings': ratings,
        'average_rating': average_rating,
        'is_favourite': is_favourite,
        'has_rated': has_rated,
    }
    return render(request, 'movie_detail.html', context)


@login_required
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        score = request.POST.get('score')

        if score:
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'score': int(score)}
            )

            if not created:
                rating.score = int(score)
                rating.save()

        return redirect('movie_detail', movie_id=movie.id)

    return render(request, 'rate_movie.html', {'movie': movie})


@login_required
def movie_reviews(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = movie.reviews.all()

    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Review.objects.create(
                user=request.user,
                movie=movie,
                content=content
            )
            return redirect('movie_reviews', movie_id=movie.id)

    return render(request, 'movie_reviews.html', {
        'movie': movie,
        'reviews': reviews
    })


def ranked(request):
    movies = Movie.objects.all()
    ranked_movies = sorted(movies, key=lambda movie: movie.average_rating(), reverse=True)
    return render(request, 'ranked.html', {'movies': ranked_movies})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)
    user_ratings = Rating.objects.filter(user=request.user)

    context = {
        'user_profile': user_profile,
        'user_reviews': user_reviews,
        'user_ratings': user_ratings,
    }
    return render(request, 'profile.html', context)


@login_required
def favourites(request):
    favourites = Favourite.objects.filter(user=request.user)
    return render(request, 'favourites.html', {'favourites': favourites})


@login_required
def add_favourite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    Favourite.objects.get_or_create(user=request.user, movie=movie)
    return redirect('movie_detail', movie_id=movie.id)


@login_required
def remove_favourite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    Favourite.objects.filter(user=request.user, movie=movie).delete()
    return redirect('favourites')


@login_required
def watch_history(request):
    history = WatchHistory.objects.filter(user=request.user)
    return render(request, 'watch_history.html', {'history': history})


@login_required
def add_watch_history(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    WatchHistory.objects.create(user=request.user, movie=movie)
    return redirect('movie_detail', movie_id=movie.id)
