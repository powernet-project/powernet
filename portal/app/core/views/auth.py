from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required

from app.models import PowernetUser, Home

def signup(request):
    print(request.POST)

    content = {}

    if request.method == 'GET':
        return render(request, 'auth/signup.html', content)

    errors = []
    content['errors'] = errors

    if not 'first_name' in request.POST or not request.POST['first_name']:
        errors.append('First name is required.')

    if not 'last_name' in request.POST or not request.POST['last_name']:
        errors.append('Last name is required.')

    if not 'password' in request.POST or not request.POST['password']:
        errors.append('Password is required.')

    if not 'confirmedpassword' in request.POST or not request.POST['confirmedpassword']:
        errors.append('Confirm password is required.')

    if 'password' in request.POST and 'confirmedpassword' in request.POST \
        and request.POST['password'] and request.POST['confirmedpassword'] \
        and request.POST['password'] != request.POST['confirmedpassword']:
        errors.append('Passwords did not match.')

    if len(User.objects.filter(username = request.POST['username'])) > 0 :
        errors.append('Username is already taken.')

    if errors:
        print(errors)
        return render(request, 'auth/signup.html', content)

    new_user = User.objects.create_user(username = request.POST['username'],\
                                        first_name = request.POST['first_name'],\
                                        last_name = request.POST['last_name'],\
                                        password = request.POST['password'])

    # create corresponding PownetUser
    newPowernetUser = PowernetUser(user=new_user, \
        first_name=new_user.first_name,\
        last_name=new_user.last_name,\
        email=request.POST['email'])
    newPowernetUser.save()

    # create the corresponding Home instance
    newHome = Home(name=new_user.username+"'s home", owner = newPowernetUser)
    newHome.save()

    # log the new user in
    new_user.save()
    new_user = authenticate(username = request.POST['username'],\
                            password = request.POST['password'])
    auth_login(request ,new_user)

    return redirect('/')


def login(request):
    print("login")
    return render(request, 'auth/login.html')

@login_required
def logout(request):
    
    return redirect('/')
