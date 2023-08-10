from django.db import models 
from django.contrib.auth.models import User
import docker 
from django.db.models.signals import post_delete
from django.dispatch import receiver


class DockerImage(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    image_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    size = models.PositiveIntegerField()    

    def __str__(self):
        return f"{self.name}:{self.tag}"


class Container(models.Model):
    
    name = models.CharField(max_length=100)
    image = models.ForeignKey(DockerImage ,  on_delete = models.CASCADE , null=True)
    owner = models.ForeignKey(User  , on_delete= models.CASCADE , related_name='containers')
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20  , choices= [('running' , 'Running') , ('stopped' , 'Stopped')])
    ip_address = models.CharField(max_length=39)
    cpu_share = models.IntegerField(default=0)
    memory_limit = models.CharField(max_length=20, default='0')


    def __str__(self):
        return self.name 


@receiver(post_delete, sender=Container)
def delete_container_on_post_delete(sender, instance, **kwargs):
    try:
        client = docker.from_env()
        container = client.containers.get(instance.name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        # Container doesn't exist, no need to delete
        pass
    except docker.errors.APIError as e:
        # Handle any other Docker API errors
        print(f"Error while deleting container: {e}")

post_delete.connect(delete_container_on_post_delete, sender=Container)

