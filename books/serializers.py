from rest_framework import serializers
from .models import Book, Author



class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta :
        model = Author
        fields = ('id', 'first_name', 'last_name', 'age', 'book_count')

    def get_book_count(self, obj):
        return obj.books.count()


class BookSerializer(serializers.ModelSerializer):
    GENRE_CHOICES = [
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('History', 'History'),
        ('Mystery', 'Mystery'),
        ('Fantasy', 'Fantasy'),
    ]

    genre = serializers.ChoiceField(choices=GENRE_CHOICES)

    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source='author', write_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'author_id', 'genre', 'page_count', 'publisher')

    def get_author(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return "Unknown"

    def validate(self, data):
        publisher_name = data.get('publisher')

        if not publisher_name and self.instance:
            publisher_name = self.instance.publisher


        books_by_publisher = Book.objects.filter(publisher=publisher_name)


        if self.instance:
            books_by_publisher = books_by_publisher.exclude(id=self.instance.id)


        if books_by_publisher.count() >= 5:
            raise serializers.ValidationError("This publisher has reached the maximum limit of 5 books.")

        return data
