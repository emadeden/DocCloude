from django.contrib import admin
from .models import Container , DockerImage 
# Register your models here.

admin.site.register(Container)
admin.site.register(DockerImage)