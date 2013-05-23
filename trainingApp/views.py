from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from models import Post, User, Author, Category, Comment
from datetime import datetime
from forms import AuthorForm, UserForm, LoginForm, PostForm, CategoryForm, CommentAuthorForm, CommentAnonymousForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from tasks import sendConfirmationMail


def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    #post.comments = Comment.objects.filter(to='p').filter(parent=post.id)

    if request.user.is_authenticated():
        cf = CommentAuthorForm(prefix="comment")
    elif request.user.is_anonymous():
        cf = CommentAnonymousForm(prefix="comment")

    return render(request,
                  'post.html', {'post': post, 'CommentForm': cf}, )


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render(request,
                  'category.html', {'category': category}, )


def posts(request):
    posts_list = Post.objects.filter(date_pub__lte=datetime.now()).order_by('-date_pub').all()
    paginator = Paginator(posts_list, 10)  # Sayfa basina 10 adet

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        posts_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        posts_list = paginator.page(paginator.num_pages)

    return render(request,
                  'posts.html', {'posts': posts_list}, )


def signUp(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        af = AuthorForm(request.POST, request.FILES, prefix='author')
        if uf.is_valid() and af.is_valid():
            user = uf.save(commit=False)
            user.is_active = True
            user.set_password(user.password)
            user.save()
            author = af.save(commit=False)
            author.user = user
            author.save()
            sendConfirmationMail.delay(user.id)
            createProfileImages(user.id)
            messages.success(request, _('Sign Up Success!'))
            messages.info(request, _('Please go to your inbox and read the activation mail'))
            return HttpResponseRedirect(reverse('pageSignUp'))
    else:
        uf = UserForm(prefix='user')
        af = AuthorForm(prefix='author')

    return render(request, 'signup.html', dict(userForm=uf, authorForm=af), )


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

                    #Session variables
                    request.session['author'] = dict(id=author.id, avatar=author.avatar, is_verified=author.is_verified,
                                                     slug=author.slug)
                    #Redirect for success
                    messages.success(request,
                                     _("Login Successful."))

                    if author.is_verified is False:
                        messages.warning(request,
                                         _("Your account not verified. Please read your mail for verify process."))
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


@login_required
def signOut(request):
    logout(request)
    messages.success(request,
                     _("Good Bye! We will miss you :("))
    return HttpResponseRedirect(reverse('pageHome'))


def profile(request, slug):
    author = Author.objects.get(slug=slug)
    if not author.is_verified:
        messages.warning(request, _('Your account not verified. Please read your mail for verify process.'))

    return render(request, 'profile.html', dict(author=author))


@login_required
def settings(request):
    return render(request, 'settings.html')


def postAdd(request):
    if request.method == "POST":
        pf = PostForm(request.POST, prefix="post")
        if pf.is_valid():
            post = pf.save(commit=False)
            post.author = Author.objects.get(pk=request.session['author']['id'])
            post.save()
            return HttpResponseRedirect(reverse("pagePost", args=(post.slug,)))
    else:
        pf = PostForm(prefix="post")
    return render(request, 'postadd.html', dict(postForm=pf))


@login_required
def categoryAdd(request):
    if request.method == "POST":
        cf = CategoryForm(request.POST, prefix="category")
        if cf.is_valid():
            cf.save()
            messages.success(request,
                             _('Category Added.'))
            return HttpResponseRedirect(reverse("pageCategoryAdd"))
    else:
        cf = CategoryForm(prefix="category")
    return render(request, 'categoryadd.html', dict(categoryForm=cf))


def confirmMail(request):
    return HttpResponse('ConfirmMail')


def commentAdd(request):
    if request.method == 'POST':

        if request.user.is_authenticated():
            cf = CommentAuthorForm(request.post, prefix="comment")
        elif request.user.is_anonymous():
            cf = CommentAnonymousForm(request.post, prefix="comment")

        if cf.is_valid():
            return
        else:
            messages.error(request,
                           _("Please fill all fields."))
            return HttpResponseRedirect(reverse('pagePost')),
    else:
        return