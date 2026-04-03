from rest_framework import serializers
from .models import Location, Zone

class ZoneSerializer(serializers.ModelSerializer): 
     class Meta: 
          model = Zone
          feilds = ['id' 'name', 'zone_type']

class LocationSerializer(serializers.ModelSerializer): 
     zones = ZoneSerializer(many=True, read_only=True)

     class Meta: 
          model = Location
          fields = ['id', 'name', 'type', 'address', 'is_active', 'zones']