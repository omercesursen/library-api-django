from celery import shared_task
from django.db.models import F
from .models import Book, Author

@shared_task

def increase_book_count(book_id):
    Book.objects.filter(id=book_id).update(read_count=F('read_count') + 1)
    book = Book.objects.get(id=book_id)
    print(f"[{book.title}] kitabinin okunma sayisi arttirildi. Guncel okuma sayisi: {book.read_count}")

    return True
@shared_task
def increase_author_ages():
    Author.objects.all().update(age=F('age') + 1)
    print("Tum yazarlarin yasi 1 arttirildi")
    return True