from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework import status
from rest_framework.decorators import action
from elasticsearch_dsl import Q
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, BookUpdateSerializer
from .tasks import increase_book_count
from .documents import BookDocument



class AuthorView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Author, pk=pk)

    def get(self, request, pk=None):
        if pk:
            author = self.get_object(pk)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        else:
            authors = Author.objects.all()
            serializer = AuthorSerializer(authors, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Method PUT not allowed without ID"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        author = self.get_object(pk)
        serializer = AuthorSerializer(author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Method DELETE not allowed without ID"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        author = self.get_object(pk)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()


    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        book_id = self.kwargs.get('pk')

        increase_book_count.delay(book_id)

        return response

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BookUpdateSerializer
        return BookSerializer

    @action(detail=False, methods=['get'])
    def random(self, request):
        random_book = Book.objects.order_by('?').first()
        if random_book:
            serializer = BookSerializer(random_book)
            return Response(serializer.data)
        return Response({"error": "No books found"}, status=status.HTTP_400_BAD_REQUEST)

class BookElasticSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        fields_param = request.query_params.get('fields', 'title,genre')

        if not query:
            return Response({"error": "Lütfen aranacak kelimeyi 'query' parametresi ile gönderin."}, status=status.HTTP_400_BAD_REQUEST)

        search_fields = fields_param.split(',')

        es_query = Q("multi_match", query=query, fields=search_fields, fuzziness="AUTO")

        search_result = BookDocument.search().query(es_query)

        response_data = []
        for hit in search_result:
            response_data.append({
                "id": hit.meta.id,
                "title": hit.title,
                "genre": hit.genre,
                "page_count": hit.page_count,
                "publisher": hit.publisher
            })

        return Response({
            "veri_kaynagi": "Elasticsearch",
            "bulunan_sonuc_sayisi": len(response_data),
            "aranan_alanlar": search_fields,
            "sonuclar": response_data
        })