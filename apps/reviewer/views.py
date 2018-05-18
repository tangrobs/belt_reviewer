from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
from django.db.models import Count

# Create your views here.
def index(request):
    return render(request,"reviewer/index.html")

def books(request):
    if not "alias" in request.session:
        messages.error(request,"You must be logged in to access that page")
        return redirect('/')
    else:
        reviews = Review.objects.all().order_by("-created_at")[:3]
        books = Book.objects.annotate(num_reviews=Count('reviews')).exclude(num_reviews = 0)
        context = {
            "reviews":reviews,
            "books":books,
        }
        return render(request,"reviewer/books.html", context)

def addbookpage(request):
    if not "alias" in request.session:
        messages.error(request,"You must be logged in to access that page")
        return redirect('/')
    else:
        authors = Author.objects.all()
        context={
            "authors":authors,
        }
        return render(request,"reviewer/add.html",context)

def showbook(request,id):
    if not "alias" in request.session:
        messages.error(request,"You must be logged in to access that page")
        return redirect('/')
    else:
        curbook = Book.objects.get(id=id)
        auth = curbook.author.name
        context = {
            "book":curbook,
            "reviews":curbook.reviews.all().order_by("-created_at"),
            "author":auth,
        }
        return render(request,"reviewer/viewbook.html", context)

def user(request,id):
    if not "alias" in request.session:
        messages.error(request,"You must be logged in to access that page")
        return redirect('/')
    else:
        curuser = User.objects.get(id = id)
        books = Book.objects.filter(reviews__reviewer__id = id).distinct()
        context = {
            "user":curuser,
            #"books":curuser.reviewed_books.all().order_by("-created_at")
            #"books":curuser.reviewed_books.annotate(num_books=Count('book')),
            "books":books,
        }
        return render(request,"reviewer/user.html",context)


def logout(request):
    request.session.clear()
    messages.success(request,"Succesfully logged out!")
    return redirect('/')

def register(request):
    if request.method == 'POST':
        validation_return = User.objects.registration_validator(request.POST)
        if "error_messages" in validation_return:
            for value in validation_return["error_messages"].values():
                messages.error(request, value)
            return redirect('/')
        elif "user" in validation_return:
            request.session['user_id'] = validation_return['user'].id
            request.session['alias'] = validation_return['user'].alias
            messages.success(request,"Succesfully registered!")
            return redirect('/books')
        else:
            print("something went wrong")
            return redirect('/')
    else:
        return redirect('/')

def login(request):
    if request.method == 'POST':
        validation_return = User.objects.login_validator(request.POST)
        if validation_return:
            request.session['user_id'] = validation_return['user'].id
            request.session['alias'] = validation_return['user'].alias
            messages.success(request,"Succesfully Logged in!")
            return redirect('/books')
        else:
            messages.error(request, "Invalid Login")
            return redirect('/')
    else:
        return redirect('/')
            
def addbook(request):
    if not checkLoggedIn(request):
        return redirect('/')

    if request.method == 'POST':
        errors = {}
        author = request.POST['selectauthor']
        if len(request.POST['title']) < 1:
            errors['title'] = "Title field cannot be blank!"
        if len(request.POST['inputauthor']):
            author = request.POST['inputauthor']
        if len(request.POST['review']) < 1:
            errors['review'] = "Please enter a review!"
        if errors:
            for value in errors.values():
                messages.error(request, value)
            return redirect('/books/add')
        else:
            messages.success(request,"Succesfully added review!")
            author_obj = Author.objects.filter(name = author)
            if not author_obj:
                Author.objects.create(name = author)
                author_obj = Author.objects.last()
            else:
                author_obj = author_obj[0]
            book_obj = Book.objects.filter(title = request.POST['title'])
            if not book_obj:
                Book.objects.create(title = request.POST['title'], author = author_obj)
                book_obj = Book.objects.last()
            elif book_obj[0].author != author_obj:
                Book.objects.create(title = request.POST['title'], author = author_obj)
                book_obj = Book.objects.last()
            else:
                book_obj = book_obj[0]            
            Review.objects.create(content = request.POST['review'], book =book_obj, rating=request.POST['rating'],\
                                reviewer = User.objects.get(id = request.session['user_id']))
            return redirect('/books/{}'.format(Book.objects.last().id))
    else:
        return redirect('/books')

def addreview(request):
    if not checkLoggedIn(request):
        return redirect('/')

    if request.method == 'POST':
        if len(request.POST['review']) < 1:
            messages.error(request, "Please enter a review!")
            return redirect('/books/{}'.format(request.POST['bookid']))
        else:
            messages.success(request, "Succesfully added review!")
            book_obj = Book.objects.get(id=request.POST['bookid'])
            Review.objects.create(content = request.POST['review'], book = book_obj, rating = request.POST['rating'],\
                                reviewer = User.objects.get(id = request.session['user_id']))
            return redirect('/books/{}'.format(request.POST['bookid']))
    else:
        return redirect('/books')

def deletereview(request, id):
    if not checkLoggedIn(request):
        return redirect('/')
    if not Review.objects.filter(id = id):
        return redirect('/books')
    book_id = Review.objects.get(id = id).book.id
    if Review.objects.get(id = id).reviewer.id == request.session['user_id']:
        Review.objects.get(id = id).delete()
        messages.success(request,"Succesfully removed review!")
        return redirect('/books/{}'.format(book_id))
    else:
        messages.error(request,"You cannot delete this review")
        return redirect('/books/{}'.format(book_id))


def checkLoggedIn(request):
    if 'user_id' not in request.session:
        return False
    return True
        
    
