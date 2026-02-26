from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    GENRE_CHOICES = [
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('History', 'History'),
        ('Mystery', 'Mystery'),
        ('Fantasy', 'Fantasy'),
    ]

    genre = serializers.ChoiceField(choices=GENRE_CHOICES)

    class Meta:
        model = Book
        fields = ('id', 'title', 'genre', 'page_count', 'publisher')

    def validate(self, data):
        publisher_name = data.get('publisher')

        book_count = Book.objects.filter(publisher=publisher_name).count()

        if book_count >= 5:
            raise serializers.ValidationError("This publisher has reached the maximum limit of 5 books.")

        return data
