from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import fields
from django.http import request
from rest_framework import serializers
from accounts.models import Comments, Profile
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

	# def validate_password(self,value):
	# 	validate_password(value)
	# 	return value

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


	# def validate_password(self, validated_data):
	# 	password1 = validated_data['password1']
	# 	password2 = validated_data['password2']
	# 	if password1 != password2:




class UserProfileSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = ['id','first_name','last_name','age','gender','contact','bio','address']


class UserSerializer(ModelSerializer):
	profile = UserProfileSerializer(many=True)
	class Meta:
		model = get_user_model()
		fields = ['id','username','email','profile','care_taker','friends']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CommentSerializer(ModelSerializer):
	class Meta:
		model = Comments
		fields = ['comment_from_user','comment_to_user','comment','parent','timestamp']
	
	def create(self, validated_data):
		return Comments.objects.create(**validated_data)