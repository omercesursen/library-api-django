from django.db import models

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')


    title = models.CharField(max_length=255, unique=True)

    genre = models.CharField(max_length=100)

    page_count = models.PositiveIntegerField()

    publisher = models.CharField(max_length=255)

    def __str__(self):
        return self.title
