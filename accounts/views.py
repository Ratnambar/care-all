from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import mixins, serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import MyUser, Profile
from accounts.serializers import SignupSerializer, LoginSerializer,UserSerializer,UserProfileSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,TokenAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes,api_view,authentication_classes
from rest_framework.permissions import IsAuthenticated



class SignupViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
	permission_classes = [AllowAny]
	queryset = MyUser.objects.all()
	serializer_class = SignupSerializer

	# def post(self,request,*args,**kwargs):
	# 	serializer = self.serializer_class(data=request.data)
	# 	serializer.is_valid(raise_exception=True)
	# 	user = serializer.validated_data['user']
	# 	token, created = Token.objects.get_or_create(user=user)
	# 	return Response({
	# 		'token':token.key,
	# 		'user_id': user.pk,
	# 		'email':user.email
	# 		})


class UserProfileView(generics.ListAPIView):
	permission_classes = [AllowAny]
	queryset = Profile.objects.all()
	serializer_class = UserProfileSerializer

class UserView(generics.ListAPIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = MyUser.objects.all()
	serializer_class = UserSerializer


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self,request):
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			user = MyUser.objects.filter(username=serializer.data['username'])
			if user:
				print(user.values()[0]['password'])
				if user.check_password(serializer.data['password']):
					token = Token.objects.get(user=user)
					return Response({'token':str(token)})
				return Response({"message":"incorrect password."})
			return Response({"message":"User does not exist."})
		return Response({'message':serializer.errors})

