from django.shortcuts import render,HttpResponse,get_object_or_404
import docker
import psutil
from .models import Container , DockerImage 
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseRedirect , JsonResponse
from .decorators import container_auth_required , user_is_authenticated , is_admin , is_numeric 
from registration.views import logUserAction_view
from registration.models import UserActionLog

# Create your views here.




def index(request):
    return render(request , 'index.html')




@user_is_authenticated
@is_admin(redirect_url='/list_images/')
def add_image(request):
    if request.method == 'POST':
        # Get the image name and tag from the form data
        image_name = request.POST['image_name']
        image_tag = request.POST['image_tag']

        # Create a Docker client object
        client = docker.from_env()

        try:
            # Pull the Docker image from the registry
            image = client.images.pull(f"{image_name}:{image_tag}")
            
            print("emad aldeen testo ")
            # Create a new DockerImage instance and save it to the database
            new_image = DockerImage(
                name=image_name,
                tag=image_tag,
                image_id=image.id,
                size=image.attrs['Size'] / (1024 * 1024), #this in MB
            ) 
            new_image.save()
            # Redirect to the list of Docker images
            logUserAction_view(request , {'action':'Add Image'})
            message = "Image installed Successfully."
            messages.info(request, message)
            return HttpResponseRedirect('/') #here we must redirect to list images 
        except docker.errors.ImageNotFound:
            # If the image does not exist, return an error message
            message = f"Image '{image_name}:{image_tag}' not found in registry" 
            messages.warning(request, message)  
            return render(request, 'add_image.html')
        except:
            # Handle all other exceptions
            message = "An error occurred while pulling the Docker image"
            messages.warning(request, message)
            return render(request, 'add_image.html')




    else:
        return render(request, 'add_image.html')





@user_is_authenticated
def delete_image(request):
    logUserAction_view(request , {'action':'Delete Image'})
    pass




@user_is_authenticated
def list_images(request):

    # Get the total amount of memory available on the host machine
    total_memory = psutil.virtual_memory().total
    total_memory_gb = total_memory / (1024 * 1024 * 1024)
    # Get the total number of CPU cores available on the host machine
    total_cores = psutil.cpu_count()

    # Calculate the maximum amount of memory and CPU share that a container can use
    max_memory = int(total_memory_gb / 2)  # Use half of the total memory
    max_cpu_share = int(100 / total_cores)  # Use equal CPU share per core

    images = DockerImage.objects.all()
    return render(request , 'list_images.html' , {'images':images , 'max_cpu_share':max_cpu_share ,'max_memory':max_memory, })




@user_is_authenticated
def list_container(request):
    containers = Container.objects.all().filter(owner = request.user)
    return render(request , 'list_container.html' , {'containers':containers ,})




@user_is_authenticated
@is_numeric('cpu_share')
@is_numeric('memory_limit')
def create_container(request , image_obj_id):
    if request.method == "POST":
        image = get_object_or_404(DockerImage , id = image_obj_id)
        container_name = request.POST.get('container_name')
        cpu_share = request.POST.get('cpu_share')
        memory_limit = request.POST.get('memory_limit')


        if Container.objects.all().filter(name = container_name).exists():
            message = "Container name is already exist change container name "
            messages.warning(request , message)
            data = {
            'success': True,
            'redirect_url': '/list_images/',  # Replace with the actual URL
            }            
            return JsonResponse(data)
        try:
            client = docker.from_env()
            container_config = {
                'image': f"{image.name}:{image.tag}",
                'detach': True,  # Run the container in detached mode
                'tty': True,  # Allocate a virtual terminal for the container
                'working_dir': '/app',
                'name': container_name,
                # 'mem_limit': memory_limit,  # Limit the container to 512MB of memory
                'ports': {},  # Assign a random port to the container
                'network_mode': 'bridge',  # Use the default bridge 
            }
            container = client.containers.create(**container_config)
            container.start()
            container.reload()



            new_container = Container(
                name=container.name,
                image= image,
                owner=request.user,
                status=container.status,
                ip_address=container.attrs['NetworkSettings']['IPAddress'],
                cpu_share=container.attrs['HostConfig']['CpuShares'],
                memory_limit=container.attrs['HostConfig']['Memory'],
                # Add other attributes as needed
            )
            new_container.save()

            logUserAction_view(request , {'action':'CreateContainer'})
            message = "Container created successfully"
            messages.info(request, message)
            # Return a JSON response with the redirect URL
            data = {
                'success': True,
                'message': 'Container created successfully',
                'redirect_url': '/list_container/',  # Replace with the actual URL
            }
            return JsonResponse(data)
        except:
            message = "Error while creating container "
            messages.warning(request , message)
            return JsonResponse({'redirect_url':'/list_images/'})
    



@user_is_authenticated
def edit_container(request):
    logUserAction_view(request , {'action':'Edit Container'})
    pass 






@user_is_authenticated
@container_auth_required
def start_container(request , container_id):
    # Get the container object from the database
    container = get_object_or_404(Container, id=container_id)

    # Create a Docker client object
    client = docker.from_env()

    # Start the container
    container_obj = client.containers.get(container.name)
    container_obj.start()

    # Update the container status in the database
    container.status = 'running'
    container.save()

    # Return a success message
    logUserAction_view(request , {'action':'StartContainer'})
    message = "Container started successfully." 
    messages.info(request, message)  
    return HttpResponseRedirect('/list_container/')
    



@user_is_authenticated
@container_auth_required
def stop_container(request , container_id):
    # Get the container object from the database
    container = get_object_or_404(Container, id=container_id)

    # Create a Docker client object
    client = docker.from_env()

    # Start the container
    container_obj = client.containers.get(container.name)
    container_obj.stop()

    # Update the container status in the database
    container.status = 'stopped'
    container.save()

    # Return a success message
    logUserAction_view(request , {'action':'Stop Container'})
    message = "Container stoped successfully."
    messages.info(request, message)
    return HttpResponseRedirect('/list_container/')
    




@container_auth_required
@user_is_authenticated
def delete_container(request , container_id):
    try:
        
        container = get_object_or_404(Container , id = container_id)
        container.delete()
        message = f"{container.name} Container Deleted Successfully"
        messages.info(request , message)
        logUserAction_view(request , {'action':'DeleteContainer'})
        data = {
            'success': True,
            'redirect_url': '/list_images/',  # Replace with the actual URL
            }            
        return JsonResponse(data)
    except Exception as e:
        message = f"{e}"
        messages.warning(request , message)
        data = {
            'success': False,
            'redirect_url': '/list_images/',  # Replace with the actual URL
            }            
        return JsonResponse(data)
    




@user_is_authenticated
def register_container(request):
    client = docker.from_env()

    # Get a list of all running containers on the host
    containers = client.containers.list()

    for container in containers:
        # Check if the container is already registered in the app
        if not Container.objects.filter(name=container.name).exists(): 
            # Create a new Container instance and save it to the database
            new_container = Container(
                name=container.name,
                owner= request.user,
                status=container.status,
                ip_address=container.attrs['NetworkSettings']['IPAddress'],
                cpu_share=container.attrs['HostConfig']['CpuShares'],
                memory_limit=container.attrs['HostConfig']['Memory'],
                # Add other attributes as needed
            )
            new_container.save()
    
    return HttpResponse('All running container is registerd in system...')








@user_is_authenticated
def register_image(request):
    client = docker.from_env()

    # Get a list of all running containers on the host
    images = client.images.list()

    for image in images:

        image_name = image.tags[0].split(':')[0]
        # Check if the container is already registered in the app
        if not DockerImage.objects.filter(name=image_name).exists(): 
            # Create a new Container instance and save it to the database
            new_image = DockerImage(
                name=image_name,
                tag=  image.tags[0].split(':')[1],
                image_id= image.id,
                size= image.attrs['Size'] / (1024 * 1024),
                # Add other attributes as needed
            )
            new_image.save()
    
    return HttpResponse('All Docker Images is registerd in system...')


@is_admin(redirect_url='/')
def user_detail(request , user_id):
    user = User.objects.all().get(id =user_id)
    containers = Container.objects.all().filter(owner  = user )
    return render(request , 'user_detail.html' , {'user': user,'containers':containers})


@is_admin(redirect_url='/')
def users_info(request):
    users = User.objects.all()
    return render(request , 'users_info.html' , {"users":users})



@is_admin(redirect_url='/')
def list_logs(request):
    if request.method == 'POST':
        selected_actions = request.POST.getlist('action')
        username = request.POST.get('username')
        logs = UserActionLog.objects.all()
        if selected_actions:
            print(selected_actions)
            logs = logs.filter(action__in = selected_actions )
        if username:
            print(logs)
            logs = logs.filter(user__username__icontains = username )
            print("emado emado emado ")
            print(logs)
    else:
        logs = UserActionLog.objects.all()
    return render(request , 'list_logs.html' , {'logs':logs})


@is_admin(redirect_url='/list_logs/')
def delete_user(request , user_id):
    try:
        user = get_object_or_404(User , id = user_id )
        user.delete()
        message = f"{user.username} Deleted Successfully"
        messages.info(request, message)
        logUserAction_view(request , {'action':'delete_user'})
        return HttpResponseRedirect('/list_logs/')
    except:
        message = f"404 Error "
        messages.warning(request, message)
        return HttpResponseRedirect('/list_logs/')
    