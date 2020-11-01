from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.TextField()  # How are the keys stored?
    public_key = models.TextField()
    # add an ID field to store the ID given by the server