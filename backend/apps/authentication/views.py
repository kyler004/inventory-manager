from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomTokenObtainPairSerializer, ChangePasswordSerializer

class LoginView(TokenObtainPairView): 
    """
    POST /auth/login/
    Uses our custom serializer that also returns user info.
    AllowAny because the user isn't authenticated yet.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs): 
        response = super().post(request, *args, **kwargs)

        # Wrap in our standard response evelope
        return Response({
            'status': 'success', 
            'data': response.data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView): 
    """
    POST /auth/logout/
    Blacklists the refresh token so it can't be used again.
    The acces token will expire naturally after 60 minutes.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        try: 
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'status': 'success', 'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception: 
            return Response (
                {'status': 'error', 'message' : 'Invalid token.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView): 
    """POST /auth/password/change/"""

    permission_classes = [IsAuthenticated]

    def post(self, request): 
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )

        if serializer.is_valid(): 
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(
                {'status': 'success', 'message': 'Password updated successfully.'}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {'status': 'error', 'details': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class MeView(APIView): 
    """
    GET /auth/me/
    Returns the currently authenticated user's profile.
    React calls this on app load to restore the session.
    """

    permission_classes=[IsAuthenticated]

    def get(self, request): 
        user = request.user
        return Response({
            'status': 'success', 
            'data' : {
                'id': user.id, 
                'name': user.name, 
                'email': user.email, 
                'role': user.role.name if user.role else None,
                'location_id': user.location_id,  
            }
        })