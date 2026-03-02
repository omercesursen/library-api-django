
İlk önce bir önceki aşamadan kalan mantık hatasını düzelttim.
Bir yayınevinin kitabını güncellerken sistem bunu yeni bir kitap ekleme gibi algılayıp 5 kitap sınırına takılıyordu
Bunu çözmek için serializers.py içindeki validate fonksiyonuna, güncelleme yaparken kontrol eden kodu ekledim.
### 1. Adım

```
if self.instance:
    books_by_publisher = books_by_publisher.exclude(id=self.instance.id)
```
### 2. Adım
Kitapları yazarlarla ilişkilendirmek için models.py dosyasına Author adında yeni bir tablo ekledim. Book tablosuna da bu yazarları bağlamak için ForeignKey yapısını kurdum. 
Böylece bir yazar silinirse kitapları da silinecek.

```
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
```
### 3. Adım
Verilerin JSON çıktısının düzgün görünmesi için serializers.py dosyasını güncelledim.
Yazarları listelerken "kaç kitabı var?" bilgisini eklemek için get_book_count metodunu yazdım.
```
class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta :
        model = Author
        fields = ('id', 'first_name', 'last_name', 'age', 'book_count')

    def get_book_count(self, obj):
        return obj.books.count()
```

Kitapları listelerken yazarın sadece ID'sini değil, adını soyadını görmek için get_author metodunu yazdım.
```
author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source='author', write_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    def get_author(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return "Unknown"
```
### 4. Adım
Yazarlar için views.py dosyasına APIView kullanarak GET, POST, PUT ve DELETE işlemlerini manuel olarak yazdım.
```
class AuthorList(APIView):
    def get (self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorDetail(APIView):
    def get_object(self, pk):
        return get_object_or_404(Author, pk=pk)

    def get (self, request, pk):
        author = self.get_object(pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    def put(self, request, pk):
        author = self.get_object(pk)
        serializer = AuthorSerializer(author, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        author = self.get_object(pk)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```
### 5. Adım
```
Kitap ismine göre arama yapabilmek için SearchFilter ekledim
action kullanarak rastgele bir kitap getiren /random/ adresini tanımladım

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    @action(detail=False, methods=['get'])
    def random(self, request):
        random_book = Book.objects.order_by('?').first()

        if random_book:
            serializer = self.get_serializer(random_book)
            return Response(serializer.data)
        return Response({"error": "No books found"}, status=status.HTTP_400_BAD_REQUEST)
```

### 6. Adım
olarak urls.py dosyasında, kitaplar ve yazarlar için gerekli adres yönlendirmelerini yaparak API'yi kullanıma hazır hale getirdim.
```
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/authors/', AuthorList.as_view()),
    path('api/authors/<int:pk>/', AuthorDetail.as_view()),
]
```