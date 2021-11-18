from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.conf import settings
from django.db.models.base import Model
from django.core.validators import RegexValidator

from django.utils.timezone import now
# Create your models here.

class MyUser(AbstractUser):
    
    care_taker = models.BooleanField(default=False)
    friends = models.ManyToManyField('self',blank=True, related_name="friends")
   

class CareSeeker(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name="careseeker")
    # funds = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=False)

    def __str__(self):
    	return self.user.username



class CareTaker(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name="caretaker")
    # profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    available_places = models.PositiveSmallIntegerField(default='0')


    def __str__(self):
    	return self.user.username


class Profile(models.Model):
    genders = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50,blank=True, null=True)
    last_name = models.CharField(max_length=50,blank=True, null=True)
    age = models.CharField(max_length=2,blank=True,null=True)
    gender = models.CharField(max_length=1, choices=genders)
    contact = models.CharField(max_length=12,blank=True, help_text='Contact phone number')
    bio = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=100, blank=True)
    # profilepic = models.ImageField(upload_to="profile/", db_index=True, default="profile/default.jpg")
    

    # def __str__(self):
    #     return self.user.username


class Friend_Request(models.Model):
    from_user = models.ForeignKey(MyUser, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(MyUser, related_name='to_user', on_delete=models.CASCADE)
    send_request = models.DateTimeField(default=now, editable=False)


    # def __str__(self):
    #     return self.from_user.username+" to "+self.to_user.username+" time "+str(self.send_request)


class Comments(models.Model):
	sno = models.AutoField(primary_key=True)
	comment = models.TextField()
	comment_from_user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name="comment_from_user")
	comment_to_user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name="comment_to_user")
	parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True)
	timestamp = models.DateTimeField(default=now)