from rest_framework import serializers
from .models import Movie, Category

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
