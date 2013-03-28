from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from models import Post, User, Author
from datetime import datetime
from forms import AuthorForm, UserForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages

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
            ## sendConfirmationMail.delay(user.id)
            ## Resim kirpilip bicilsin, isimlendirilip kayit guncellensin - Kuyruktan update edilsin -
            messages.success(request, _('Sign Up Success!'))
            messages.info(request, _('Please go to your inbox and read the activation mail'))
            return HttpResponseRedirect(reverse('pageSignUp'))
    else:
        uf = UserForm(prefix='user')
        af = AuthorForm(prefix='author')

    return render(request, 'signup.html', dict(userForm=uf, authorForm=af),)


def signIn(request):
    if request.method == 'POST':
        lf = LoginForm(request.POST, prefix='login')
        if lf.is_valid():
            email = lf.cleaned_data['email']
            password = lf.cleaned_data['password']

            user = authenticate(username=email, password=password)

            if user is not None:
                if user.is_active:
                    author = Author.objects.get(user=user)

                    if not author.DoesNotExist:
                        messages.error(request,
                                       _("This user have not any author profile."))
                        return HttpResponseRedirect(reverse("pageSignIn"))

                    login(request, user)

                    #Redirect for success
                    messages.success(request,
                                     _("Login Successful."))

                    if author.is_verified is False:
                        messages.warning(request, _("Your account not verified."))
                        return HttpResponseRedirect(reverse('pageProfile', args=(user.id,)))

                    return HttpResponseRedirect(reverse('pageHome'))
                else:
                    messages.error(request,
                                   _("This account is not active."))
                    return HttpResponseRedirect(reverse('pageSignIn'))
            else:
                messages.error(request,
                               _("Please enter a correct username and password."))
                return HttpResponseRedirect(reverse('pageSignIn'))
    else:
        lf = LoginForm(prefix='login')
    return render(request, 'signin.html', dict(loginForm=lf))


def signOut(request):
    logout(request)
    messages.success(request,
                     _("Good Bye! We will miss you :("))
    return HttpResponseRedirect(reverse('pageHome'))


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    author = Author.objects.get(user=user)
    # ba nin authoru yok. onu eslestir, calisacaktir
    return render(request, 'profile.html')


def confirmMail(request):
    return HttpResponse('ConfirmMail')