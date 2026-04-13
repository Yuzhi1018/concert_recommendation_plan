from django.db import models
from django.conf import settings

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pref_travel = models.IntegerField(default=5)
    pref_time = models.IntegerField(default=5)
    pref_cost = models.IntegerField(default=5)
    pref_safety = models.IntegerField(default=5)
    pref_environment = models.IntegerField(default=5)
    pref_artist = models.IntegerField(default=5)
    pref_affection = models.IntegerField(default=5)

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artist = models.CharField(max_length=255)
    budget = models.IntegerField(null=True, blank=True)
    top_city = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.artist}"
    def __str__(self):
        return f"{self.user.username}'s preferences"
    