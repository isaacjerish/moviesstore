from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to="movie_images/")
    release_year = models.IntegerField(default=2000)
    director = models.CharField(max_length=100, default="Unknown")  # <-- ADD THIS LINE
    genre = models.CharField(max_length=50, default="Action")  # <-- ADD THIS LINE
    rating = models.CharField(max_length=10, default="PG")  # <-- ADD THIS LINE

    def __str__(self):
        return str(self.id) + " - " + self.name


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " - " + self.movie.name


class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')  # Prevent duplicate ratings from same user on same movie

    def __str__(self):
        return f"{self.user.username} - {self.movie.name} - {self.rating} stars"