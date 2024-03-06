from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register the viewset with it.
router = DefaultRouter()
router.register(r'messages', views.MessageViewSet, basename='messages')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    path('staffs/', views.staff_users_list, name='staffs'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('conversation/', views.DisplayMessageView.as_view(), name='display_message'),
    path('user/', views.user_details_view, name='user_details'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('received-messages/', views.ReceivedMessagesAPIView.as_view(), name='received_messages'),
    path('messageslists/', views.MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('messageslists/<int:pk>/', views.MessageRetrieveUpdateDestroyAPIView.as_view(), name='message-detail'),
    path('users/messaged/<int:sender_id>/', views.UsersWhoMessagedSpecificUserAPIView.as_view(), name='users-messaged-specific'),
]

# Include the router's URLs
urlpatterns += router.urls
