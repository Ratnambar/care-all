from os import name
from django.urls import include, path
from rest_framework import routers
from accounts.views import SignupViewSet, UserView, UserProfileView,LoginView,send_friend_request,accept_friend_request,cancel_friend_request



router = routers.DefaultRouter()
router.register('signup', SignupViewSet),



urlpatterns=[
	path('',include(router.urls)),
	path('userdetail/',UserView.as_view(),name="user_detail"),
	path('userprofile/', UserProfileView.as_view(), name="profile_detail"),
	path('login/', LoginView.as_view(),name="login_view"),
	path('send_request/<int:userID>/', send_friend_request,name="send_request"),
	path('accept_request/<int:requestID>/', accept_friend_request, name='accept_request'),
	path('cancel_request/<int:requestID>/',cancel_friend_request,name='cancel_request')

]