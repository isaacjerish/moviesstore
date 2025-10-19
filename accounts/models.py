from django.db import models
from django.contrib.auth.models import User
from regions.models import State


class UserProfile(models.Model):
    """Extended user profile to store user's state"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.state.name if self.state else 'No State'}"
