from rest_framework import serializers
from .models import Location, Zone

class LocationSerializer(serializers.ModelSerializer): 
     class Meta: 
          model = Location
          feilds = []