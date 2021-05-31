import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm, RenewBookModelForm

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

# LoginRequiredMixin plays the same role as @login_required decorator
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksListView(PermissionRequiredMixin, LoanedBooksByUserListView):
    permission_required = ('catalog.can_mark_returned')

    def get_context_data(self, **kwargs):
        context = super(LoanedBooksListView, self).get_context_data(**kwargs)
        context['show_borrower'] = True
        return context

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')    

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

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

# Generic editing views for Author
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_birth': '01/01/1900'}
    permission_required = ('catalog.can_mark_returned')
    # standard template name is "model_name_form.html", _form part can be redefined
    # template_name_suffix = '_editform' 

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = ('catalog.can_mark_returned')

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = ('catalog.can_mark_returned')
    # standard template name is "model_name_confirm_delete.htmll"

# Generic editing views for Book
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = ('catalog.can_mark_returned')

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = ('catalog.can_mark_returned')

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = ('catalog.can_mark_returned')