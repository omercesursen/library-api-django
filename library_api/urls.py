from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, AuthorView
from books.views import BookElasticSearchView

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/authors/', AuthorView.as_view(), name='author-list'),

    path('api/authors/<int:pk>/', AuthorView.as_view(), name='author-detail'),
    path('books/elasticsearch/', BookElasticSearchView.as_view(), name='book-elasticsearch'),
]