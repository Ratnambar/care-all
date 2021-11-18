from django.urls import include, path
from rest_framework import routers
from accounts.views import SignupViewSet, UserView, UserProfileView,LoginView
# from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)



router = routers.DefaultRouter()
router.register('signup', SignupViewSet),



urlpatterns=[
	path('',include(router.urls)),
	# path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('userdetail/',UserView.as_view(),name="user_detail"),
	path('userprofile/', UserProfileView.as_view(), name="profile_detail"),
	path('login/', LoginView.as_view(),name="login_view"),

]