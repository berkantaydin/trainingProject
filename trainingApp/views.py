from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from models import Post
from datetime import datetime
from forms import UserForm
from forms import AuthorForm
from forms import LoginForm
from tasks import sendConfirmationMail


def post(request, post_id):
    return HttpResponse(post_id)


def posts(request):
    return render(request,
                  'posts.html', {'posts': Post.objects.filter(date_pub__lte=datetime.now()).order_by('-date_pub')[:5]},)


def signUp(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        af = AuthorForm(request.POST, request.FILES, prefix='author')
        if uf.is_valid() and af.is_valid():
            user = uf.save(commit=False)
            user.is_active = False
            user.set_password(user.password)
            user.save()
            author = af.save(commit=False)
            author.user = user
            author.save()
            ## Kuyruga yolla mail atilsin -> user.mail -> activation mail send
            ## Resim kirpilip bicilsin, isimlendirilip kayit guncellensin - Kuyruktan update edilsin -
            return HttpResponseRedirect('/activation_information/')
    else:
        uf = UserForm(prefix='user')
        af = AuthorForm(prefix='author')

    return render(request, 'signup.html', dict(userForm=uf, authorForm=af),)


def signIn(request):
    if request.method == 'POST':
        lf = LoginForm(request.POST, prefix='login')
        if lf.is_valid():
            # Authenticating process.
            return HttpResponseRedirect('profile')
    else:
        lf = LoginForm(prefix='login')
    return render(request, 'signin.html', dict(loginForm=lf))


def confirmMail(request):
    return HttpResponse('ConfirmMail')