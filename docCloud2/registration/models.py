from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User 

class UserActionLog(models.Model):
    action = models.CharField(max_length=100)
    user= models.ForeignKey(User, on_delete= models.CASCADE , null=True )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"