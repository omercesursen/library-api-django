from rest_framework import serializers
from django.core.cache import cache #
from .models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'age', 'book_count')

    def get_book_count(self, obj):
        return obj.books.count()

    def validate(self, attrs):
        if self.instance:
            if 'age' in attrs:
                attrs.pop('age')
        return attrs


class BookSerializer(serializers.ModelSerializer):
    GENRE_CHOICES = [
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('History', 'History'),
        ('Mystery', 'Mystery'),
        ('Fantasy', 'Fantasy'),
    ]

    genre = serializers.ChoiceField(choices=GENRE_CHOICES)

    author = AuthorSerializer(read_only=True)

    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        write_only=True
    )

    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'author_id', 'genre', 'page_count', 'publisher')


    def validate(self, data):
        if not self.instance:
            publisher_name = data.get('publisher')
            if publisher_name:
                cache_key = f"publisher_count_{publisher_name}"

                book_count = cache.get(cache_key)

                if book_count is None:
                    book_count = Book.objects.filter(publisher=publisher_name).count()
                    cache.set(cache_key, book_count, timeout=3600)
                    print(f"DEBUG: Veri DB'den cek'ld' ve Cache'e yazildi: {book_count}")
                else:
                    print(f"DEBUG: Veri REDIS Cache'den okundu {book_count}")
                if book_count >= 5:
                    raise serializers.ValidationError("This publisher has reached the maximum limit of 5 books.")

        return data
    def create(self, validated_data):
        book = super().create(validated_data)
        cache_key = f"publisher_count_{book.publisher}"
        cache.delete(cache_key)
        print(f"DEBUG: Cache imha edildi: {cache_key}")
        return book

class BookUpdateSerializer(serializers.ModelSerializer):
    GENRE_CHOICES = [
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('History', 'History'),
        ('Mystery', 'Mystery'),
        ('Fantasy', 'Fantasy'),
    ]
    genre = serializers.ChoiceField(choices=GENRE_CHOICES)

    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        write_only=True
    )

    class Meta:
        model = Book
        fields = ('id', 'title', 'author_id', 'genre', 'page_count', 'publisher')
        read_only_fields = ('title',)

    def validate(self, data):
        instance = self.instance
        publisher_name = data.get('publisher', instance.publisher)

        books_by_publisher = Book.objects.filter(publisher=publisher_name).exclude(id=instance.id)

        if books_by_publisher.count() >= 5:
            raise serializers.ValidationError("This publisher has reached the maximum limit of 5 books.")

        return data