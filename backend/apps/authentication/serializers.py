# Authentication serializers
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    """
    Extends the default JWT login serializer. 
    By default it only returns acces + refresh tokens.
    We also return user info so React doesn't need a second API call to knwo who just logged in.
    Connects to: POST /auth/login/ from our API design.
    """

    def validate(self, attrs): 
        # Call parent- does the actual credential check
        data = super().validate(attrs)

        #Append user info to the response
        data['user'] = {
            'id': self.user.id, 
            'name': self.user.name, 
            'email': self.user.email, 
            'role': self.user.role.name if self.user.role else None, 
            'location_id': self.user.location_id, 
        }

        return data

class ChangePasswordSerializer(serializers.Serializer):
    """Handles POST /auth/password/change/"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value): 
        user = self.context['request'].user
        if not user.check_password(value): 
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate_new_password(self, value): 
        """
        Basic password strength check.
        In production you'd use a library like django-password-validators.
        """

        if value.isdigit(): 
            raise serializers.ValidationError(
                "Password cannot be entirely numeric."
            )
        return value; 
