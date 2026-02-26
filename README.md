
# Library Management API

### 1. Adım
Bilgisayarımda `djangodeneme` klasörünü açıp sanal ortamımı kurdum ve gerekli kütüphaneleri yükledim.
```
python -m venv env
env\Scripts\activate
pip install django djangorestframework
```

 
### 2. Adım
Django iskeletini oluşturmak için ve uygulamayı(app) oluşturmak için bu komutları sırayla giriyorum
``` 
django-admin startproject library_api .
python manage.py startapp books
```
### 3. Adım
Bunları yaptıktan sonra library_api/setting.py'nin içindeki INSTALLED_APPS listesine 'rest_framework' ve 'books' ekledim
### 4. Adım
Kitapların başlığı, türü, sayfa sayısı ve yayınevi gibi özelliklerini tanımlayan bir veritabanı şeması oluşturmak için books/models.py içine şu kodları yazarak veritabanı tablomu hazırlıyorum 
```
class Book(models.Model):
    title = models.CharField(max_length=255, unique=True)
    genre = models.CharField(max_length=100)
    page_count = models.IntegerField()
    publisher = models.CharField(max_length=255)

    def __str__(self):
        return self.title
```
### 5. Adım
books/serializers.py dosyasını oluşturup içine gerekli kodları yazıyorum. Burada serializer kullanarak veritabanındaki verileri JSON formatına dönüştürüyoruz.
Ayrıca ChoiceField ile kitap türlerini kısıtlıyoruz ve validate fonksiyonu ile bir yayınevinin 5 kitaptan  fazla eklememesini engelleyen bir kod yazıyoruz.
```
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
```
### 6. Adım
Sonrasıda books/views.py dosyasına CRUD işlemlerini tanımlayan ModelViewSet yapısını ekliyoruz
```
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```
### 7. Adım
library_api/urls.py üzerinden internet tarayıcısından veya postmanden hangi adrese gidince apinin çalışacağını belirliyoruz 
```
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
```
### 8. Adım
Yazdığımız verilerin veritabanında birer tabloya dönüşebilmesi için bu 2 komudu çalıştırıyorum
```
python manage.py makemigrations

python manage.py migrate
```
Sonrasında .gitignore adında bir dosya oluşturup içine internete yüklemek istemediğimiz dosyaları yazıyoruz
