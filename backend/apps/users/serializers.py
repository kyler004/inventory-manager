from rest_framework import serializers
from .models import User, Role

class RoleSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer): 
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), 
        source='role', 
        write_only=True # Accepted on input, not shown in output
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta: 
        model = User
        fields = [
            'id', 'name', 'role', 'role_id', 'location', 'is_active', 'password', 
            'created_at'
        ]
        read_only_fields = ['created_at']

        def create(self, validated_data): 
            """
            Overrids create to properly hash the password.
            NEVER store plain text passwords.
            """
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password) #Hashes via django's auth system
            user.save()
            return user
        
        def update(self, instance, validate_data): 
            """Hash password on update too, if provided."""
            password = validate_data.pop('password',None)
            if password: 
                instance.set_password(password)
            return super().update(instance, validate_data)