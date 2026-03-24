from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    poster = models.URLField(blank=True)
    description = models.TextField()
    cast = models.TextField(blank=True)

    def average_rating(self):
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        return avg if avg is not None else 0

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reviewed {self.movie.title}"


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favourited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} favourited {self.movie.title}"


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_histories')
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-watched_at']

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"
