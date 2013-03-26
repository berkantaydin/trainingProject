from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from models import Post
from datetime import datetime
from forms import UserForm
from forms import AuthorForm

def post(request, post_id):
    return HttpResponse(post_id)


def posts(request):
    return render(request,
                  'posts.html', {'posts': Post.objects.filter(date_pub__lte=datetime.now()).order_by('-date_pub')[:5]},)


def signUp(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        af = AuthorForm(request.POST, prefix='author')
        if uf.is_valid() and af.is_valid():
            #validation burada olacak
            user = uf.save()
            author = af.save(commit=False)
            author.user = user
            author.save()
            return HttpResponseRedirect('/testtooo/')
    else:
        uf = UserForm(prefix='user')
        af = AuthorForm(prefix='author')

    return render(request, 'signup.html', dict(userForm=uf, AuthorForm=af),)


def signIn(request):
    return HttpResponse('signin')


def confirmMail(request):
    return HttpResponse('ConfirmMail')