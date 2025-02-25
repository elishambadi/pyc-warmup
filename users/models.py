from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ChoirMember(models.Model):
    USER_ROLES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default="member")
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"