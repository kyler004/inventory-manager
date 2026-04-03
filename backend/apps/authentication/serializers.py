# Authentication serializers
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer): 
    """
    Extends the default JWT login serializer. 
    
    """