from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(min_length=3)
