from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime


def index(request):
	"""
	View function for the home page
	"""

	# Generate counts of some of the main objects
	num_books=Book.objects.all().count()
	num_instances=BookInstance.objects.all().count()
	# Available books (status = 'a')
	num_instances_available=BookInstance.objects.filter(status__exact='a').count()
	num_authors=Author.objects.count()


	# Number of visits to this view, as counted in the session
	num_visits=request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits+1

	# Render the Html template index.html with the data in the context variable

	return render(
		request,
		'index.html',
		context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,
		'num_authors':num_authors,'num_visits':num_visits}, # num_visits appended
		)


from django.views import generic

class BookListView(generic.ListView):
    model = Book
    template_name = 'book_list.html'
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book_detail.html'



class LibrarianBookView(PermissionRequiredMixin,generic.ListView):
	model = BookInstance
	template_name = 'borrowed_book_list.html'
	permission_required = 'catalog.librarian'

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	"""
	Genric clas-based view listing books on loan to current user.
	"""
	model = BookInstance
	template_name = 'bookinstance_list_borrowed_user.html'
	paginate_by = 10


	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from .forms import RenewBookForm


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


