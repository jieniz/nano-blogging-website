from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.db.models import Max

class Post(models.Model):
    post = models.CharField(max_length=42)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post

    @staticmethod
    def get_max_time():
        return Post.objects.all().aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

    @staticmethod
    def get_max_time_follower(req_user):
        profile=Profile.objects.get(user=req_user)
        followees = profile.followees.all()
        posts = Post.objects.filter(user__in=followees).distinct()
        return posts.aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

    @staticmethod
    def get_max_time_profile(profile_user):
        posts = Post.objects.filter(user=profile_user).distinct()
        return posts.aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

    @staticmethod
    def update(time="1970-01-01T00:00+00:00"):
        posts = Post.objects.filter(last_changed__gt=time).distinct()
        return posts

    @staticmethod
    def update_follower(req_user, time="1970-01-01T00:00+00:00"):
        profile=Profile.objects.get(user=req_user)
        followees = profile.followees.all()
        posts = Post.objects.filter(user__in=followees, last_changed__gt=time).distinct().order_by("time")
        return posts

    @staticmethod
    def update_profile(profile_user, time="1970-01-01T00:00+00:00"):
        posts = Post.objects.filter(user=profile_user, last_changed__gt=time).distinct().order_by("time")
        return posts

    @property
    def html(self):
        return render_to_string("post.html", {"user":self.user,"post":self.post,"time":self.time,"post_id":self.id}).replace("\n", "");


class Comment(models.Model):
    content = models.CharField(max_length=42)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

    @staticmethod
    def update(id, changeTime="1970-01-01T00:00+00:00"):
        post = Post.objects.get(id=id)
        comms = Comment.objects.filter(post=post, last_changed__gt=changeTime).distinct().order_by("time")
        return comms

    @property
    def html(self):
        return render_to_string("comment.html", {"user":self.user,"content":self.content,"time":self.time,"comment_id":self.id}).replace("\n", "");

    @staticmethod
    def get_max_time():
        return Comment.objects.all().aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

    @staticmethod
    def get_max_time_follower(post_id):
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post).distinct()
        return comments.aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

class Profile(models.Model):
    age = models.IntegerField()
    bio = models.CharField(max_length=420, default="Say something about yourself here.", blank=True)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="profile_pictures",default="profile.png")
    followees = models.ManyToManyField(User,related_name='following')
