from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Petition(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    movie_title = models.CharField(max_length=255)
    movie_year = models.IntegerField(null=True, blank=True)
    movie_director = models.CharField(max_length=100, null=True, blank=True)
    movie_genre = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    votes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-votes_count', '-created_at']
        unique_together = ['movie_title', 'created_by']  # Prevent duplicate petitions by same user
    
    def __str__(self):
        return f"{self.title} - {self.votes_count} votes"
    
    @property
    def is_expired(self):
        """Check if petition is older than 7 days"""
        return timezone.now() > (self.created_at + timedelta(days=7))
    
    @property
    def is_active(self):
        """Check if petition is still active (not expired and pending)"""
        return not self.is_expired and self.status == 'pending'
    
    def update_votes_count(self):
        """Update the votes_count field based on actual votes"""
        self.votes_count = self.vote_set.count()
        self.save(update_fields=['votes_count'])


class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['petition', 'user']  # One vote per user per petition
    
    def __str__(self):
        return f"{self.user.username} voted on {self.petition.title}"