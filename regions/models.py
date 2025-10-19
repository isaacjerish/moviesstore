from django.db import models
from movies.models import Movie


class State(models.Model):
    """US States for geographic movie popularity tracking"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)
    center_lat = models.FloatField(help_text="Latitude for map centering")
    center_lng = models.FloatField(help_text="Longitude for map centering")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class MoviePopularity(models.Model):
    """Track movie popularity by state"""
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    purchase_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['movie', 'state']
        ordering = ['-purchase_count', '-view_count']
    
    def __str__(self):
        return f"{self.movie.name} in {self.state.name} ({self.purchase_count} purchases)"
    
    @property
    def total_activity(self):
        """Combined score for ranking"""
        return self.purchase_count + (self.view_count * 0.1)  # Views weighted less than purchases