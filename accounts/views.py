from rest_framework.authtoken.models import Token
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import Friend_Request, MyUser, Profile, Comments
from accounts.serializers import SignupSerializer, LoginSerializer,UserSerializer,UserProfileSerializer \
	,ForgotPasswordSerializer,ResetPasswordEmailSerializer,ChangePasswordSerializer,CommentSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes,api_view,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator




# global otp
# otp = random.randint(1000, 9999)



def verify_email(email):
	try:
		email = MyUser.objects.get(email=email)
	except Exception:
		return False
	else:
		return True


def send_email(email):
	if verify_email(email):
		try:
			send_mail(
				"Registration on my website.",
				"Congratulations !. You have successfully registered.",
				"cvctest51@gmail.com",
				[email],
				fail_silently=False,
			)
		except Exception:
			return Response({"message": "email couldn't send."})
		else:
			return Response({"message": "Email sent. !"})
	return Response({"message": "Email is not registered."})
	

# def send_otp(email, otp):
# 	try:
# 		send_mail(
# 			"Registration on my website.",
# 			f"<p>Your OTP for forgot password is : {globals()['otp']}</p>",
# 			"cvctest51@gmail.com",
# 			[email],
# 			fail_silently=False,
# 		)
# 	except:
# 		return Response({"message": "email couldn't send."})
	

# Signup view
class SignupViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
	queryset = MyUser.objects.all()
	serializer_class = SignupSerializer
	permission_classes = [AllowAny]

	def create(self, request, *args, **kwargs):
		try:
			MyUser.objects.get(email=request.POST.get('email'))
		except:
			serializer = SignupSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				send_email(request.POST.get('email'))
				return Response({"message":"You have successfully registered."})
			return Response({"message":serializer.errors})
		return  Response({"message":"This email is already registered."})


# User profile view
class UserProfileView(generics.ListAPIView):
	permission_classes = [AllowAny]
	queryset = Profile.objects.all()
	serializer_class = UserProfileSerializer


# User view for nested view containg user and profile details.
class UserView(generics.ListAPIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = MyUser.objects.all()
	serializer_class = UserSerializer


# Login view.
class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self,request):  # sourcery skip: raise-from-previous-error
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			try:
				user = MyUser.objects.get(username=serializer.data['username'])
			except BaseException as e:
				raise ValidationError({"message":"user does not exist."})
			if user:
				if user.check_password(serializer.data['password']):
					token = Token.objects.get(user=user)
					return Response({'token':str(token)})
				return Response({"message":"incorrect password."})
			return Response({"message":"User does not exist."})
		return Response({'message':serializer.errors})


# view for sending request.We are using id of the user to whom request
#  to be send and current user id,who is sending request.
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def send_friend_request(request,userID):
	from_user = request.user
	from_user_details = MyUser.objects.get(id=request.user.id)
	print(from_user)
	to_user = MyUser.objects.get(id=userID)
	print(to_user)
	if from_user == to_user:
		return Response("you can't send request to yourself.")
	else:
		if(len(from_user_details.friends.all())>=4 or len(to_user.friends.all())>=4):
			return Response({'message':'you or {to_user} has already four connection.'.format(to_user=to_user)})
		else:
			friend_request, created = Friend_Request.objects.get_or_create(
				from_user=from_user, to_user=to_user
			)
			result = {'from_user':from_user,'to_user':to_user}
			if created:
				return Response({'message':'Friend request has been sent.'})
			else:
				return Response({'message':'Friend request has already sent.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
	user = request.data
	email = request.data.get('email')
	print(email)
	try:
		email = MyUser.objects.get(email=request.data.get('email'))
	except Exception:
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			send_email(request.data.get('email'))
			serializer.save()
			return Response({"message": "user created successfully."})
		return Response({"message": serializer.errors})
	return Response({"message":"Email is already registered."})


# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def forgot_password(request):
# 	serializer = ForgotPasswordSerializer(data=request.data)
# 	if serializer.is_valid():
# 		user = request.user
# 		if user.check_password(serializer.data.get('old_password')):
# 			user.set_password(serializer.data.get('new_password'))
# 			user.save()
# 			update_session_auth_hash(request, user)
# 			return Response({"message": "Password changed successfully."})
# 		return Response({"message": "Incorrect old password."})
# 	return Response({"message": serializer.errors})
	# print(request.user, request.data.get('email'))
	# user = request.user
	# email = request.data.get('email')
	# token = Token.objects.get(user=user)
	# if token:
	# 	send_email(email)
	# 	return Response({"message": "Password reset link has been sent to your email."})
	# return Response({"message": "Token not found."})
# 	try:
# 		fetch_email = MyUser.objects.get(email=request.data.get('email'))
# 	except Exception:
# 		return Response({"message": "This email not found.Please enter registered email address."})
# 	else:
# 		# print(request.user)
# 		token = Token.objects.filter(user=request.user.id).first()
		
# 		return Response({"message": "Okay"})
		# send_email(request.data.get('email'), globals()['otp'])


# @api_view(['POST'])
# def verify_otp(request):
# 	if int(request.data.get('otp')) == int(globals()['otp']):
# 		return Response({"message": "otp verified."})
# 	return Response({"message": "otp not verified."})
            

# Request accept view.
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def accept_friend_request(request,requestID):
	print(requestID)
	# for accepting request I need the requestID(the Id of the friend request related
	#  to the current user from Friend Request table).
	friend_request = Friend_Request.objects.get(from_user=requestID)
	if friend_request.to_user == request.user:
		friend_request.to_user.friends.add(friend_request.from_user)
		friend_request.from_user.friends.add(friend_request.to_user)
		friend_request.delete()
		return Response({'message':'Request has been accepted.'})
	return Response({'message':'Request is not accepted.'})


# View for canceling of friend request.
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cancel_friend_request(request,requestID):
	friend_request = Friend_Request.objects.get(id=requestID)
	if friend_request.to_user == request.user:
		friend_request.delete()
		return Response({'message':'Friend request has been canceled.'})
	return Response({'message':'Friend request can not be cancel.'})


# Simple view for changing user password.
class UpdatePasswordView(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]

	def get_object(self,queryset=None):
		return self.request.user

	def put(self,request, *args, **kwargs):
		self.object = self.get_object()
		serializer = ChangePasswordSerializer(data=request.data)
		if serializer.is_valid():
			old_password = serializer.data.get('old_password')
			if not self.object.check_password(old_password):
				return Response({'old_password':['Wrong Password']},status=status.HTTP_400_BAD_REQUEST)
			self.object.set_password(serializer.data.get('new_password'))
			self.object.save()
			return Response({'message':'password has been changed successfully.'},status=status.HTTP_201_CREATED)
		return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def comments_view(request,comment_to_userID):
	comment_from_user = request.user.id
	comment_to_user = MyUser.objects.get(id=comment_to_userID)
	parent_sno = request.data.get('parent_sno') #frontend will send parent_sno(comment.sno) from hidden input field.
	if parent_sno == "":
		comments_data = {
			'comment_from_user':comment_from_user,'comment_to_user':comment_to_user.id,
			'comment':request.data.get('comment')
		}
		serializer = CommentSerializer(data=comments_data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message':"Your comment has been send successfully."})
		return Response({"message":"Your comment could not be sent."})
	else:
		parent = Comments.objects.get(sno=parent_sno)
		comments_data = {
			'comment_from_user':comment_from_user,'comment_to_user':comment_to_user.id,
			'comment':request.data.get('comment'),'parent':parent
		}
	# print(comments_data)
	serializer = CommentSerializer(data=comments_data)
	# print(serializer)
	if serializer.is_valid():
		# print(serializer)
		serializer.save()
		return Response({'message':"Your reply has been send successfully."})
	return Response({"message":"Your reply could not be sent."})