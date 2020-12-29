from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Book, BookInstance, Author, Genre
from catalog.forms import RenewBookModelForm
import datetime

def index(request):
    """View function for home page of site."""
    
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    
    # # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    form_class = RenewBookModelForm
    form = form_class(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            
            return HttpResponseRedirect(reverse('the-borrowed'))
        
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})
        
    context = {
        'form': form,
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    
    def get_queryset(self):
        return Book.objects.all()[:10]
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'These are just some data'
        return context
    
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    context_object_name = 'author_list'
    template_name = 'catalog/author_list.html'
    
    def get_queryset(self):
        return Author.objects.all()

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksByStaffsListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/book_list_borrowed_staff.html'
    permission_required = 'catalog.can_mark_returned'
    raise_exception = True
    context_object_name = "bookinstance_list"
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    
class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    
class BookCreate(CreateView):
    model = Book
    fields = '__all__'#['title', 'author', 'summary', 'isbn', 'genre']
    
class BookUpdate(UpdateView):
    model = Book
    fields = '__all__' #['title', 'author', 'summary', 'isbn', 'genre']
    
class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')