from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    experience_choices = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    experience_level = models.CharField(max_length=20, choices=experience_choices, default='beginner')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null= True)
    timezone = models.CharField(max_length=60, default='UTC')
    dark_mode = models.BooleanField(default=False)
    