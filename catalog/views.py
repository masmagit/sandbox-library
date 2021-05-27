from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'   # name for a template variable (standard would be book_list)
    template_name = 'catalog/objects_list.html'  # Custom template name and location
    paginate_by = 2

    def get_queryset(self):
        return Book.objects.all()[:10] # Get first 10 books

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['title'] = "Books List"
        context['model'] = self.model._meta.model_name
        context['no_data'] = "There are no books in the library."
        return context

class BookDetailView(generic.DetailView):
    model = Book

    def inFuncBasedView(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/objects_list.html'

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['title'] = "Authors List"
        context['model'] = self.model._meta.model_name
        context['no_data'] = "There are no authors."
        return context

class AuthorDetailView(generic.DetailView):
    model = Author


def index(request):
    """View function for home page of site."""
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    else:
        request.session.set_test_cookie()
    
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    
    word = "Life"
    num_books_word = Book.objects.filter(title__icontains=word).count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_word': (word, num_books_word),
        'num_visits': num_visits,
    }

    return render(request, 'catalog/index.html', context=context)
