from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Create your models here.
class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        if len(postData['name']) < 2:
            errors['name_len'] = "First name must be at least 2 characters"
        #need to change this to accept spaces as well
        """ elif not postData['first_name'].isalpha():
            errors['f_name_alpha'] = "First name must be only letters" """
        if len(postData['alias']) < 1:
            errors['alias_len'] = "Alias cannot be blank!"
        if len(postData['email']) < 1:
            errors['l_email'] = "Email Cannot be blank!"
        elif not EMAIL_REGEX.match(postData['email']):
            errors['inv_email'] = "Invalid Email!"
        elif User.objects.filter(email = postData['email']):
            errors['dupl_email'] = "Email already exists."
        if len(postData['password']) < 8:
            errors['pword_len'] = "Password must be at least 8 characters"
        elif postData['password'] != postData['password_confirm']:
            errors['mm_pword'] = "Passwords do not match"
        if errors:
            return {"error_messages":errors}
        else:
            phash = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
            User.objects.create(name=postData['name'], alias=postData['alias'],\
                                email = postData['email'], pass_hash = phash)
            return {"user":User.objects.last()}
    
    def login_validator(self, postData):
        user = User.objects.filter(email = postData['email'])
        if user:
            if bcrypt.checkpw(postData['password'].encode(),user[0].pass_hash.encode()):
                return {"user":user[0]}
            return False
        else:
            return False
            
            

class User(models.Model):
    name = models.CharField(max_length = 255)
    alias = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    pass_hash = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Author(models.Model):
    name = models.CharField(max_length = 255)
    objects = UserManager()

class Book(models.Model):
    title = models.CharField(max_length = 255)
    author = models.ForeignKey(Author, related_name = "authored_book")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Review(models.Model):
    content = models.TextField()
    rating = models.IntegerField()
    book = models.ForeignKey(Book, related_name = "reviews")
    reviewer = models.ForeignKey(User, related_name = "reviewed_books")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()


