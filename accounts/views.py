from rest_framework.authtoken.models import Token
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import Friend_Request, MyUser, Profile, Comments, Rating
from accounts.serializers import SignupSerializer, LoginSerializer,UserSerializer,UserProfileSerializer \
	,ForgotPasswordSerializer,ResetPasswordEmailSerializer,ChangePasswordSerializer,CommentSerializer\
	,RatingSerializer
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
from django.db.models import Sum, Count



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

	def list(self, request):
		if request.user.care_taker:
			users = MyUser.objects.exclude(care_taker=True).exclude(username='admin')\
				 .annotate(total_rating=Count('received_ratings__rating')) # type: ignore
		else:
			users = MyUser.objects.exclude(care_taker=False).exclude(username='admin')\
				.annotate(total_rating=Count('received_ratings__rating'))
		# users_rating = users.annotate(total_rating=Sum('received_ratings__rating'))
		# print('User rating ',users[0].__dict__)
		serializer = UserSerializer(users, many=True)
		return Response({'current_user': serializer.data})


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
	to_user = MyUser.objects.get(id=userID)
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
	serializer = CommentSerializer(data=comments_data)
	if serializer.is_valid():
		serializer.save()
		return Response({'message':"Your reply has been send successfully."})
	return Response({"message":"Your reply could not be sent."})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def give_rating(request, rated_userID):
	rated_user = MyUser.objects.get(id=rated_userID)
	rating = request.data.get('rating')
	if request.user.id == rated_user.id:
		return Response({"message":"You can't give rating to yourself."})
	if rating < 0 or rating > 4:
		return Response({"message":"Rating should be between 0 to 4"})
	if Rating.objects.filter(user=request.user, rated_user=rated_user).exists():
		return Response({"message":"You have already given a rating to this user."})
	data = {
		'user':request.user.id, 'rated_user':rated_user.id, 'rating':rating
	}
	serializer = RatingSerializer(data=data)
	if serializer.is_valid():
		serializer.save()
		return Response({"message":"Rating has been given successfully."})
	return Response({"message":"Your rating couldn't save."})