from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from api.models import UserProfile
from api.serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserProfileUpdateSerializer


class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request: Request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        user_serializer = UserSerializer(user)
        refresh = RefreshToken.for_user(user)

        return Response({'access_token': str(refresh.access_token), 'refresh': str(refresh), 'user': user_serializer.data}, status=status.HTTP_201_CREATED)


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
                "message": "Login successful"
            })
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            refresh_token = RefreshToken(refresh_token)
            refresh_token.blacklist()
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
