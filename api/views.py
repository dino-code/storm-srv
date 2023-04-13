from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from api.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import UserProfile
from .serializers import UserProfileUpdateSerializer
        

class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            if user:
                refresh_token = RefreshToken.for_user(user)
                access_token = AccessToken.for_user(user)
                refresh_token = str(refresh_token)
                access_token = str(access_token)
                user_serializer = UserSerializer(user)
                return Response({
                    'user': user_serializer.data,
                    'access': str(access_token),
                    'refresh': str(refresh_token),
                    "message": "Registration successful"
                })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'user': user_serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response({"message": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                new_access_token = str(token.access_token)
                token.refresh()
                return Response({"access": new_access_token})
            except TokenError:
                return Response({"message": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)
