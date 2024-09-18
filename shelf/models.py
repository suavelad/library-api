from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from library.model import BaseModel
from users.models import User


class Author(BaseModel):
    GENDER = (("male", "Male"), ("female", "Female"))

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    email = models.EmailField()
    created_by = models.ForeignKey(User, related_name="author_creator", on_delete=models.SET_NULL,null=True)

    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Book(BaseModel):
    title = models.TextField()
    description = models.CharField(max_length=255)
    pages = models.BigIntegerField(null=True)
    author = models.ForeignKey(Author, related_name="authors", on_delete=models.DO_NOTHING)
    isbn = models.CharField(null=True)
    genre = models.CharField(null=True)
    keywords  = models.CharField(null=True)
    created_by = models.ForeignKey(User, related_name="book_creators", on_delete=models.SET_NULL,null=True)


    def __str__(self) -> str:
        return f"{self.title} by {self.author.fullname}"
    

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        constraints = [
            models.CheckConstraint(check=models.Q(book__isnull=False), name='book_not_null'),
        ]

    def save(self, *args, **kwargs):
        if self.user.favorites.count() >= 20:
            raise ValueError("You can only have 20 favorite books.")
        super().save(*args, **kwargs)