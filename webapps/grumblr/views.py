from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator

from grumblr.models import *
from grumblr.forms import *

from django.http import HttpResponse, Http404
from django.urls import reverse
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from mimetypes import guess_type
from django.views.decorators.csrf import csrf_exempt

def log_in(request):
    context={}
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'grumblr/login.html', context)
    form = LoginForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/login.html', context)   
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')
    user = authenticate(request, username=username, password=password)
    login(request, user)
    return redirect(home)

@login_required
def home(request):
    context={}
    posts = Post.objects.all().order_by("-time")
    context['posts'] = posts
    context['user'] = request.user
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404
    followees = profile.followees.all()
    context['followees'] = followees
    return render(request, 'grumblr/global_stream.html', context)

@login_required
def follower_stream(request):
    context={}
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404
    followees = profile.followees.all()
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    context['posts'] = posts
    context['user'] = request.user
    context['followees'] = followees
    return render(request, 'grumblr/follower_stream.html', context)

@login_required
def profile(request, username):
    context = {}
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    posts_of_user = Post.objects.filter(user=post_user).order_by("-time")
    try:
        post_user_profile = Profile.objects.get(user=post_user)
    except ObjectDoesNotExist:
        post_user_profile = Profile.objects.create(age=0, user=post_user, bio='Say something about yourself.')
    followees = Profile.objects.filter(user=request.user).get().followees.all()
    context["followees"] = followees
    context['posts'] = posts_of_user
    context['profile'] = post_user_profile
    return render(request, 'grumblr/profile.html', context)

@login_required
def follow(request, username):
    context = {}
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    try:
        request_user_profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404
    request_user_profile.followees.add(post_user);
    request_user_profile.save()
    request_user_followees=request_user_profile.followees.all()
    post_user_profile=Profile.objects.get(user=post_user)
    followees = post_user_profile.followees.all()
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    context['posts'] = posts
    context["user"] = post_user
    context['profile'] = post_user_profile
    context["followees"] = request_user_followees
    return render(request, 'grumblr/profile.html', context)

@login_required
def unfollow(request, username):
    context = {}
    try:
        post_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise Http404
    profile.followees.remove(post_user);
    profile.save()
    request_user_followees = profile.followees.all();
    post_user_profile=Profile.objects.get(user=post_user)
    followees = post_user_profile.followees.all()
    posts = Post.objects.filter(user__in=followees).order_by("-time")
    context['posts'] = posts
    context["user"] = post_user
    context['profile'] = post_user_profile
    context["followees"] = request_user_followees
    return render(request, 'grumblr/profile.html', context)

@login_required
def edit_profile(request):
    context = {}
    user = request.user

    try:
        profile = Profile.objects.get(user=user)
    except ObjectDoesNotExist:
        profile = Profile.objects.create(age=0, user=user, bio='Say something about yourself.')

    if request.method == 'GET':
        context['form'] = EditProfileForm()
        context['profile'] = profile
        return render(request, 'grumblr/edit_profile.html', context)

    form = EditProfileForm(request.POST, request.FILES)
    context['form'] = form

    if not form.is_valid():
        context['profile'] = profile
        return render(request, 'grumblr/edit_profile.html', context)

    posts_of_user = Post.objects.filter(user=request.user).order_by("-time")

    if form.cleaned_data['age']:
        profile.age=form.cleaned_data['age']
    if form.cleaned_data['bio']:
        profile.bio=form.cleaned_data['bio']
    if form.cleaned_data['picture']:
        profile.picture = form.cleaned_data['picture']
    if form.cleaned_data['first_name']:
        user.first_name = form.cleaned_data['first_name']
    if form.cleaned_data['last_name']:
        user.last_name = form.cleaned_data['last_name']

    profile.save()
    request.user.save()

    context = {'posts' : posts_of_user, 'user' : user, 'profile' : profile}
    return render(request, 'grumblr/profile.html', context)

@login_required
def photo(request, username):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404
    try:
        profile = Profile.objects.get(user=user)
    except ObjectDoesNotExist:
        raise Http404

    if not profile.picture:
        raise Http404
    content_type = guess_type(profile.picture.name)
    return HttpResponse(profile.picture, content_type=content_type)

@transaction.atomic
def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'grumblr/signup.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/signup.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'], \
                                        password=form.cleaned_data['password1'], \
                                        first_name=form.cleaned_data['firstname'], \
                                        last_name=form.cleaned_data['lastname'],
                                        email=form.cleaned_data['email'],
                                        is_active=False)
    new_user.save()
    token = default_token_generator.make_token(new_user)

    email_body="""
    Click this link to confirm your email address and complete setup for your account:
    https://%s%s
    """ % (request.get_host(), 
           reverse('confirm', args=(new_user.username, token)))
        
    send_mail('Verify your account | Grumblr', email_body, 'jieniz@andrew.cmu.edu', [new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'grumblr/email_confirmation.html', context)

@transaction.atomic
def reset_password(request):
    context = {}
    if request.method == 'GET':
        context['form'] = EmailResetForm()
        return render(request, 'grumblr/reset_password.html', context)

    form = EmailResetForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/reset_password.html', context)
    
    user= User.objects.get(username=form.cleaned_data['username'])
    token = default_token_generator.make_token(user)

    email_body="""
    Click this link to confirm your email address and complete setup for your account:
    https://%s%s
    """ % (request.get_host(), 
           reverse('confirm', args=(user.username, token)))
        
    send_mail('Verify your account | Grumblr', email_body, 'jieniz@andrew.cmu.edu', [user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'grumblr/reset_confirmation.html', context)

@transaction.atomic
def reset_confirmation(request, username, token):
    context = {}
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    if not default_token_generator.check_token(user, token):
        raise Http404
    context['user'] = user
    return redirect(log_in)

@transaction.atomic
def confirmation(request, username, token):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        raise Http404

    if not default_token_generator.check_token(user, token):
        raise Http404
    user.is_active=True
    user.save()
    new_profile = Profile(age=0, user=user, bio='Say something about yourself.')
    new_profile.save()
    return redirect(log_in)

@login_required()
def change_password(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ChangePasswordForm()
        return render(request, 'grumblr/change_password.html', context)
    form = ChangePasswordForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/change_password.html', context)
    password = form.cleaned_data['password']
    user = authenticate(username=request.user.username, password=password)
    if user is None:
        context['error'] = "error"
        return render(request, 'grumblr/change_password.html', context)
    user = request.user
    user.set_password(form.cleaned_data['password1'])
    user.save()
    return redirect(log_in)

@login_required
def add_post(request):
    errors = []
    # Creates a new item if it is present as a parameter in the request
    if not 'post' in request.POST or not request.POST['post']:
        errors.append('You must enter an item to add.')
        posts = Post.objects.all().order_by("-time")
        return render(request, 'grumblr/global_stream.html', {'posts' : posts, 'errors' : errors})

    else:
        new_post = Post(post=request.POST['post'], user=request.user)
        new_post.save()

        posts = Post.objects.all().order_by("-time")

        context = {'posts' : posts, 'errors' : errors, 'user' : request.user}
        return render(request, 'grumblr/global_stream.html', context)

# hw5 newly added
@login_required
def post(request):
    context = {}
    if request.method == 'GET':
        context['form'] = PostForm()
        return render(request, 'grumblr/global_stream.html', context)
    form = PostForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/global_stream.html', context)
    new_post = Post(post=form.cleaned_data['post'], user=request.user)
    new_post.save()
    posts = Post.objects.all().order_by("-time")
    context['posts'] = posts
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
@transaction.atomic
@csrf_exempt
def add_comment(request, post_id):
    context = {}
    if request.method == 'GET':
        context['form'] = CommentForm()
        return render(request, 'grumblr/global_stream.html', context)

    form = CommentForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/global_stream.html', context)

    try:
        post = Post.objects.get(id=post_id)
    except ObjectDoesNotExist:
        return HttpResponse("The post did not exist")

    new_comment = Comment(content=form.cleaned_data['comment'], user=request.user, post=post)
    new_comment.save()
    comments = Comment.objects.filter(post=post).order_by("-time")
    context['comments'] = comments

    return render(request, 'comments.json', context, content_type='application/json')

# automatically update posts and comment every five seconds
# unix start time: 1970-01-01T00:00+00:00
@login_required
@transaction.atomic
def update(request, time="1970-01-01T00:00+00:00"):
    if time == 'undefined':
        time="1970-01-01T00:00+00:00"
    max_time = Post.get_max_time()
    posts = Post.update(time)
    context = {"max_time":max_time, "posts":posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
@transaction.atomic
def update_follower(request, time="1970-01-01T00:00+00:00"):
    if time == 'undefined':
        time="1970-01-01T00:00+00:00"
    max_time = Post.get_max_time_follower(request.user)
    posts = Post.update_follower(request.user, time)
    context = {"max_time":max_time, "posts":posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
@transaction.atomic
def update_profile(request, username, time="1970-01-01T00:00+00:00"):
    if time == 'undefined':
        time="1970-01-01T00:00+00:00"
    profile_user = User.objects.get(username=username)
    max_time = Post.get_max_time_profile(profile_user)
    posts = Post.update_profile(profile_user, time)
    context = {"max_time":max_time, "posts":posts}
    return render(request, 'posts.json', context, content_type='application/json')

@login_required
@transaction.atomic
def update_comments(request, post_id, time="1970-01-01T00:00+00:00"):
    if time == 'undefined':
        time="1970-01-01T00:00+00:00"
    max_time = Comment.get_max_time()
    comments = Comment.update(post_id, time)
    context = {"max_time":max_time, "comments":comments}
    return render(request, 'comments.json', context, content_type='application/json')
