from rest_framework import serializers

from . import models


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        exclude = ("created_by",)


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        exclude = ("created_by",)
