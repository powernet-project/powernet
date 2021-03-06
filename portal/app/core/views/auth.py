from app.models import PowernetUser, Home
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate


def signup(request):
    content = {}

    if request.method == 'GET':
        return render(request, 'auth/signup.html', content)

    errors = []
    content['errors'] = errors
    content["lastPOST"] = request.POST

    if 'first_name' not in request.POST or not request.POST['first_name']:
        errors.append('First name is required.')

    if 'last_name' not in request.POST or not request.POST['last_name']:
        errors.append('Last name is required.')

    if 'password' not in request.POST or not request.POST['password']:
        errors.append('Password is required.')

    if 'confirmedpassword' not in request.POST or not request.POST['confirmedpassword']:
        errors.append('Confirm password is required.')

    if 'password' in request.POST and 'confirmedpassword' in request.POST \
            and request.POST['password'] and request.POST['confirmedpassword'] \
            and request.POST['password'] != request.POST['confirmedpassword']:
        errors.append('Passwords did not match.')

    if User.objects.filter(username__iexact=request.POST['username']).count() > 0:
        errors.append('Username is already taken.')

    if PowernetUser.objects.filter(email__iexact=request.POST["email"]).count() > 0:
        errors.append("Email address has been used.")

    if errors:
        return render(request, 'auth/signup.html', content)

    new_user = User.objects.create_user(username=request.POST['username'],
                                        first_name=request.POST['first_name'],
                                        last_name=request.POST['last_name'],
                                        password=request.POST['password'])

    # create corresponding PowernetUser
    new_powernet_user = PowernetUser(user=new_user,
                                     first_name=new_user.first_name,
                                     last_name=new_user.last_name,
                                     email=request.POST['email'])
    new_powernet_user.save()

    # create the corresponding Home instance
    new_home = Home(name=new_user.username + "'s home", owner=new_powernet_user)
    new_home.save()

    # log the new user in
    new_user.save()
    new_user = authenticate(username=request.POST['username'], password=request.POST['password'])
    auth_login(request, new_user)

    return redirect('/')


def login(request):
    if request.method == 'GET':
        return render(request, 'auth/login.html')

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return redirect('/')

    content = {'errors': ['Invalid credentials']}
    return render(request, 'auth/login.html', content)



@login_required
def logout(request):
    auth_logout(request)
    return redirect('/login')
