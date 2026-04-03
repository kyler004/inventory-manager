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

