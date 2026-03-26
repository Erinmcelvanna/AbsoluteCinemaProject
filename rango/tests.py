from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, Movie, Rating, Review, Favourite, WatchHistory


# Helpers
def create_user(username='testuser', password='testpass123'):
    user = User.objects.create_user(username=username, password=password)
    UserProfile.objects.get_or_create(user=user)
    return user

def create_movie(title='Test Film', year=2024):
    return Movie.objects.create(
        title=title,
        year=year,
        description='A test film.',
        poster='https://example.com/poster.jpg',
    )


# Model Tests

class UserProfileModelTest(TestCase):

    def test_profile_str(self):
        user = create_user('alice')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'alice')

    def test_profile_linked_to_user(self):
        user = create_user()
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user.username, 'testuser')


class MovieModelTest(TestCase):

    def test_movie_str(self):
        movie = create_movie('Anora')
        self.assertEqual(str(movie), 'Anora')

    def test_average_rating_no_ratings_returns_zero(self):
        # New repo returns 0 (not None) when no ratings exist
        movie = create_movie()
        self.assertEqual(movie.average_rating(), 0)

    def test_average_rating_with_ratings(self):
        movie = create_movie()
        user1 = create_user('user1')
        user2 = create_user('user2')
        Rating.objects.create(user=user1, movie=movie, score=2)
        Rating.objects.create(user=user2, movie=movie, score=4)
        self.assertEqual(movie.average_rating(), 3.0)


class RatingModelTest(TestCase):

    def test_rating_str(self):
        user = create_user()
        movie = create_movie('Conclave')
        Rating.objects.create(user=user, movie=movie, score=4)
        rating = Rating.objects.get(user=user, movie=movie)
        self.assertIn('testuser', str(rating))
        self.assertIn('Conclave', str(rating))

    def test_rating_unique_per_user_movie(self):
        user = create_user()
        movie = create_movie()
        Rating.objects.create(user=user, movie=movie, score=3)
        with self.assertRaises(Exception):
            Rating.objects.create(user=user, movie=movie, score=5)


class ReviewModelTest(TestCase):

    def test_review_str(self):
        user = create_user()
        movie = create_movie('The Brutalist')
        Review.objects.create(user=user, movie=movie, content='Magnificent.')
        review = Review.objects.get(user=user, movie=movie)
        self.assertIn('testuser', str(review))
        self.assertIn('The Brutalist', str(review))


class FavouriteModelTest(TestCase):

    def test_favourite_str(self):
        user = create_user()
        movie = create_movie('Nosferatu')
        fav = Favourite.objects.create(user=user, movie=movie)
        self.assertIn('testuser', str(fav))
        self.assertIn('Nosferatu', str(fav))

    def test_favourite_unique_per_user_movie(self):
        user = create_user()
        movie = create_movie()
        Favourite.objects.create(user=user, movie=movie)
        with self.assertRaises(Exception):
            Favourite.objects.create(user=user, movie=movie)


class WatchHistoryModelTest(TestCase):

    def test_watch_history_str(self):
        user = create_user()
        movie = create_movie('Flow')
        wh = WatchHistory.objects.create(user=user, movie=movie)
        self.assertIn('testuser', str(wh))
        self.assertIn('Flow', str(wh))


# View Tests

class IndexViewTest(TestCase):

    def test_index_loads(self):
        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/index.html')


class HomeViewTest(TestCase):

    def test_home_loads(self):
        response = self.client.get(reverse('rango:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/home.html')


class DiscoverViewTest(TestCase):

    def test_discover_loads(self):
        response = self.client.get(reverse('rango:discover'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/discover.html')

    def test_discover_no_query_returns_all_movies(self):
        create_movie('Anora')
        create_movie('Conclave')
        response = self.client.get(reverse('rango:discover'))
        self.assertIn('Anora', response.context['movies'])
        self.assertIn('Conclave', response.context['movies'])

    def test_discover_query_filters_results(self):
        create_movie('Anora')
        create_movie('Conclave')
        response = self.client.get(reverse('rango:discover'), {'q': 'Anora'})
        self.assertIn('Anora', response.context['movies'])
        self.assertNotIn('Conclave', response.context['movies'])

    def test_discover_query_case_insensitive(self):
        create_movie('The Brutalist')
        response = self.client.get(reverse('rango:discover'), {'q': 'brutalist'})
        self.assertIn('The Brutalist', response.context['movies'])

    def test_discover_no_match_returns_empty(self):
        create_movie('Anora')
        response = self.client.get(reverse('rango:discover'), {'q': 'zzznomatch'})
        self.assertEqual(response.context['movies'], [])


class MovieDetailViewTest(TestCase):

    def test_movie_detail_loads(self):
        create_movie('Flow')
        response = self.client.get(reverse('rango:movie_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/movieDetail.html')


# Profile redirects when logged out

class ProfileAuthRedirectTest(TestCase):

    def test_profile_redirects_when_logged_out(self):
        response = self.client.get(reverse('rango:profile'))
        # Should redirect to login, not silently show empty page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])


# Profile when logged in

class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client.login(username='testuser', password='testpass123')

    def test_profile_loads_when_logged_in(self):
        response = self.client.get(reverse('rango:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/profile.html')

    def test_profile_shows_favourite_movies(self):
        movie = create_movie('Poor Things')
        Favourite.objects.create(user=self.user, movie=movie)
        response = self.client.get(reverse('rango:profile'))
        self.assertIn('Poor Things', response.context['favourite_movies'])

    def test_profile_shows_recently_watched(self):
        movie = create_movie('Past Lives')
        WatchHistory.objects.create(user=self.user, movie=movie)
        response = self.client.get(reverse('rango:profile'))
        self.assertIn('Past Lives', response.context['recently_watched'])

    def test_profile_recently_watched_capped_at_four(self):
        for i in range(6):
            m = create_movie(f'Movie {i}')
            WatchHistory.objects.create(user=self.user, movie=m)
        response = self.client.get(reverse('rango:profile'))
        self.assertLessEqual(len(response.context['recently_watched']), 4)


# Register

class RegisterViewTest(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse('rango:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/register.html')

    def test_register_valid_data_creates_user(self):
        self.client.post(reverse('rango:register'), {
            'email':     'new@example.com',
            'username':  'newuser',
            'password1': 'securepass99',
            'password2': 'securepass99',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_creates_user_profile(self):
        self.client.post(reverse('rango:register'), {
            'email':     'new@example.com',
            'username':  'newuser',
            'password1': 'securepass99',
            'password2': 'securepass99',
        })
        user = User.objects.get(username='newuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_register_logs_user_in_and_redirects_to_profile(self):
        response = self.client.post(reverse('rango:register'), {
            'email':     'new@example.com',
            'username':  'newuser',
            'password1': 'securepass99',
            'password2': 'securepass99',
        })
        self.assertRedirects(
            response,
            reverse('rango:profile'),
            fetch_redirect_response=False
        )

    def test_register_mismatched_passwords_shows_error(self):
        response = self.client.post(reverse('rango:register'), {
            'email':     'new@example.com',
            'username':  'newuser',
            'password1': 'securepass99',
            'password2': 'differentpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username_shows_error(self):
        create_user('existinguser')
        response = self.client.post(reverse('rango:register'), {
            'email':     'another@example.com',
            'username':  'existinguser',
            'password1': 'securepass99',
            'password2': 'securepass99',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_register_missing_fields_shows_error(self):
        response = self.client.post(reverse('rango:register'), {
            'email':     '',
            'username':  '',
            'password1': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)


# Login

class LoginViewTest(TestCase):

    def setUp(self):
        create_user('loginuser', 'mypassword')

    def test_login_page_loads(self):
        response = self.client.get(reverse('rango:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/login.html')

    def test_valid_login_redirects_to_profile(self):
        response = self.client.post(reverse('rango:login'), {
            'username': 'loginuser',
            'password': 'mypassword',
        })
        self.assertRedirects(
            response,
            reverse('rango:profile'),
            fetch_redirect_response=False
        )

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('rango:login'), {
            'username': 'loginuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_invalid_login_does_not_authenticate(self):
        self.client.post(reverse('rango:login'), {
            'username': 'loginuser',
            'password': 'wrongpassword',
        })
        # User should not be logged in
        response = self.client.get(reverse('rango:profile'))
        self.assertEqual(response.status_code, 302)



# Logout

class LogoutViewTest(TestCase):

    def test_logout_redirects_to_index(self):
        create_user()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('rango:logout'))
        self.assertRedirects(
            response,
            reverse('rango:index'),
            fetch_redirect_response=False
        )

    def test_logout_actually_logs_user_out(self):
        create_user()
        self.client.login(username='testuser', password='testpass123')
        self.client.get(reverse('rango:logout'))
        # After logout, profile should redirect (user no longer authenticated)
        response = self.client.get(reverse('rango:profile'))
        self.assertEqual(response.status_code, 302)