from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from rest_framework import generics, permissions, status,viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView


from django.http import HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from api.models import User, Message
from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    MessageSerializer,
    UserSerializer,
    DisplayMessageSerializer,
)

class UsersWhoMessagedSpecificUserAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Require authentication

    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        messages_sent = Message.objects.filter(sender=sender_id)
        messages_received = Message.objects.filter(receiver=sender_id)
        receiver_ids_sent = [message.receiver.id for message in messages_sent]
        sender_ids_received = [message.sender.id for message in messages_received]
        all_ids = set(receiver_ids_sent + sender_ids_received)
        
        # Filter the queryset to exclude superusers and staff users
        return User.objects.filter(id__in=all_ids, is_superuser=False, is_staff=False)


class MessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_details_view(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)
# Get All Routes

@api_view(['GET'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=404)

    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = "Hello buddy"
        data = f'Congratulation your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([AllowAny])
def staff_users_list(request):
    # Filter users with staff status equal to 1
    staff_users = User.objects.filter(is_staff=1)
    serializer = UserSerializer(staff_users, many=True)
    return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['post'])  # Use detail=False as this is not a detail action
    def send_message(self, request):
        receiver_id = request.data.get('receiver_id')
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'Receiver user not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create a new message instance with sender and receiver
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, receiver=receiver)
            return Response({'message': 'Message sent successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class DisplayMessageView(APIView):
    """
    Display messages between specific sender and receiver
    """
    permission_classes = [AllowAny]

    def get(self, request):
        sender_id = request.query_params.get('sender_id')
        receiver_id = request.query_params.get('receiver_id')

        if sender_id is None or receiver_id is None:
            return Response({"error": "Both sender_id and receiver_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        messages = Message.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).order_by('sent_time')

        serializer = DisplayMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ReceivedMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Retrieve messages where the current user is the receiver
        received_messages = Message.objects.filter(receiver=request.user)

        # Serialize the messages
        serializer = MessageSerializer(received_messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# class UnreadMessageCountDetailView(APIView):
#     """
#     View to retrieve the count of unread messages for a specific sender and receiver.
#     """

#     def get(self, request, sender_id, receiver_id, format=None):
#         # Get the queryset for unread message count for the specified sender and receiver
#         unread_messages_count = MessageReadStatus.objects.filter(message__sender=sender_id, message__receiver=receiver_id, is_read=False).count()

#         # Create a dictionary to store sender and receiver IDs with their unread message counts
#         unread_counts_dict = {
#             'sender_id': sender_id,
#             'receiver_id': receiver_id,
#             'unread_count': unread_messages_count
#         }

#         return Response(unread_counts_dict, status=status.HTTP_200_OK)