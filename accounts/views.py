from re import A
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import mixins, serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import Friend_Request, MyUser, Profile, Comments
from accounts.serializers import SignupSerializer, LoginSerializer,UserSerializer,UserProfileSerializer,ChangePasswordSerializer,CommentSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes,api_view,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# Signup view
class SignupViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
	permission_classes = [AllowAny]
	queryset = MyUser.objects.all()
	serializer_class = SignupSerializer

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

	def post(self,request):
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