from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, AuthorList, AuthorDetail

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/authors/', AuthorList.as_view(), name='author-list'),
    path('api/authors/<int:pk>/', AuthorDetail.as_view(), name='author-detail'),
]
