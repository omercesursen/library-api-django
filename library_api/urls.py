from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, AuthorView  # Sadece AuthorView'i çağırdık

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/authors/', AuthorView.as_view(), name='author-list'),

    path('api/authors/<int:pk>/', AuthorView.as_view(), name='author-detail'),
]