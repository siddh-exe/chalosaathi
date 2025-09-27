from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserProfile(AbstractUser):  
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    aadhaar = models.CharField(max_length=14, unique=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male","Male"), ("Female","Female"), ("Other","Other")]
    )
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")

    # make email the username field
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"   # authentication uses email
    REQUIRED_FIELDS = ["username", "phone", "aadhaar"]  # still require these when creating a superuser

    def __str__(self):
        return self.full_name

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"