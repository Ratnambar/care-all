from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import fields, Count
from django.http import request
from rest_framework import serializers
from accounts.models import Comments, Profile, Rating
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer, Serializer


class SignupSerializer(ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ['username','email','password','care_taker']
		extra_kwargs = {
			'password':{'write_only':True}
		}

	def validate(self, attrs):
		if attrs['username'] == '':
			raise serializers.ValidationError({"message":"Username field can't be blank."})
		if attrs['email'] == '' or '@' not in attrs['email']:
			raise serializers.ValidationError({"message":"Enter a valid email address."})
		if attrs['password'] == '' or len(attrs['password']) < 8:
			raise serializers.ValidationError({"message":"Password length should be greater than 8 characters."})
		return super().validate(attrs)

	def create(self,validate_data):
		user = get_user_model()(**validate_data)
		user.set_password(validate_data['password'])
		user.save()
		return user


class LoginSerializer(Serializer):
	username = serializers.CharField(required=True)
	password = serializers.CharField(required=True)


class ForgotPasswordSerializer(Serializer):
	old_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)


class ResetPasswordEmailSerializer(Serializer):
	email = serializers.EmailField(required=True)


class UserProfileSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = ['id','first_name','last_name','age','gender','contact','bio','address']


class UserSerializer(ModelSerializer):
	profile = UserProfileSerializer(many=True)
	total_rating = serializers.SerializerMethodField()

	class Meta:
		model = get_user_model()
		fields = ['id','username','email','profile','care_taker','friends','total_rating']

	def get_total_rating(self, obj):
		return obj.received_ratings.aggregate(total_rating=Count('rating'))['total_rating'] or 0


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CommentSerializer(ModelSerializer):
	class Meta:
		model = Comments
		fields = ['comment_from_user','comment_to_user','comment','parent','timestamp']
	
	def create(self, validated_data):
		return Comments.objects.create(**validated_data)
	

class RatingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Rating
		fields = ('user', 'rated_user', 'rating', 'created_at')
	
	def create(self, validated_data):
		return Rating.objects.create(**validated_data)