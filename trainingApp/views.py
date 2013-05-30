from Carbon.Menus import keyContextualMenuModifiers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from models import Post, User, Author, Category, Comment
from datetime import datetime
from forms import AvatarForm, UserForm, LoginForm, PostForm, CategoryForm, CommentAuthorForm, CommentAnonymousForm, \
    UserEmailForm, UserPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from tasks import sendConfirmationMail, createProfileImages, updateComments, sendCommentConfirmationMail
import random


def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    #post.comments = Comment.objects.filter(to='p').filter(parent=post.id)

    if request.user.is_authenticated():
        cf = CommentAuthorForm(prefix="comment",
                               initial={'parent_id': post.id,
                                        'parent_type': ContentType.objects.get_for_model(post).id})
    elif request.user.is_anonymous():
        cf = CommentAnonymousForm(prefix="comment",
                                  initial={'parent_id': post.id,
                                           'parent_type': ContentType.objects.get_for_model(post).id})

    comments = Comment.objects.filter(is_pending=False).filter(base_post=post.id).order_by('parent_id').order_by(
        'date_pub').all()

    return render(request,
                  'post.html', {'post': post, 'comments': comments, 'CommentForm': cf}, )


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_list = Post.objects.filter(date_pub__lte=datetime.now()).filter(category=category).order_by('-date_pub').all()
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
                  'category-posts.html', {'category': category, 'posts': posts_list}, )


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
        af = AvatarForm(request.POST, request.FILES, prefix='author')
        if uf.is_valid() and af.is_valid():
            user = uf.save(commit=False)
            user.is_active = True
            user.set_password(user.password)
            user.save()
            author = af.save(commit=False)
            author.user = user
            author.save()
            sendConfirmationMail.delay(user.id)
            createProfileImages.delay(user.id)
            messages.success(request, _('Sign Up Success!'))
            messages.info(request, _('Please go to your inbox and read the activation mail'))
            return HttpResponseRedirect(reverse('pageHome'))
    else:
        uf = UserForm(prefix='user')
        af = AvatarForm(prefix='author')

    return render(request, 'signup.html', dict(userForm=uf, avatarForm=af), )


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
                        return HttpResponseRedirect(reverse('pageProfile', args=(author.slug,)))

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
    return render(request, 'profile.html', dict(author=author))


@login_required
def settings(request):
    author = Author.objects.get(slug=request.session['author']['slug'])

    if not author.is_verified:
        messages.warning(request, _('Your account not verified. Please read your mail for verify process.'))

    user = author.user

    upf = UserPasswordForm(prefix='password')
    uaf = AvatarForm(prefix='avatar')
    uef = UserEmailForm(prefix='email')

    if request.method == "POST":

        if request.POST['type'] == "change_password":
            upf = UserPasswordForm(request.POST, prefix='password')
            if upf.is_valid():
                author = upf.save()
                createProfileImages.delay(user.id)
                messages.success(request, _('Password Changed !'))
                return HttpResponseRedirect(reverse('pageSettings'))
        elif request.POST['type'] == "change_email":
            uef = UserEmailForm(request.POST, prefix='email')
            if uef.is_valid():
                user.email = uef.save()
                author.is_verified = False
                author.save()
                sendConfirmationMail.delay(user.id)
                messages.success(request, _('Email Change Success!'))
                messages.info(request, _('Please go to your inbox and read the re-activation mail'))
                return HttpResponseRedirect(reverse('pageSettings'))
        elif request.POST['type'] == "change_avatar":
            uaf = AvatarForm(request.POST, request.FILES, prefix='avatar')
            if uaf.is_valid():
                author = uaf.save()
                messages.success(request, _('Avatar Changed, You look good!'))
                return HttpResponseRedirect(reverse('pageSettings'))

    return render(request, 'settings.html', dict(upf=upf, uef=uef, uaf=uaf))


@login_required
def postAdd(request):
    if request.method == "POST":
        pf = PostForm(request.POST, prefix="post")
        if pf.is_valid():
            post = pf.save(commit=False)
            post.author = Author.objects.get(pk=request.session['author']['id'])
            post.save()
            cache.clear()
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


def confirmMail(request, key):
    author = get_object_or_404(Author, key_activation=key, is_verified=False)
    author.is_verified = True
    author.save()
    '''Mail adresine tanimli comment'leri tasi'''
    updateComments.delay(author.id)
    messages.success(request, _('Account Validated ! If you have any comment with this email, will be updating all.'))
    return HttpResponseRedirect(reverse("pageHome"))


def confirmCommentWithMail(request, post_id, comment_id, key):
    comment = get_object_or_404(Comment, id=comment_id, key=key, is_pending=True)
    comment.is_pending = False
    comment.save()
    messages.success(request, _('Comment Validated !'))
    return HttpResponseRedirect(reverse("pagePost", args=(Post.objects.get(post_id))))


def deleteAccount(request):
    author = Author.objects.get(slug=request.session['author']['slug'])

    if not author.is_deleted:
        author.is_deleted = True
        messages.warning(request, _('Your account deleted. :('))

    return HttpResponseRedirect(reverse("pageHome"))


def commentAdd(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated():
            cf = CommentAuthorForm(request.POST, prefix="comment")
        elif request.user.is_anonymous():
            cf = CommentAnonymousForm(request.POST, prefix="comment")

        if cf.is_valid():
            if request.user.is_authenticated():
                comment = CommentAuthorForm(request.POST, prefix="comment")
                comment = comment.save(commit=False)
                comment.base_post = Post.objects.get(slug=slug)
                comment.author = request.user.author
                comment.is_pending = False
                comment.save()
                messages.success(request, _("Comment Adding Success !"))
                return HttpResponseRedirect(reverse("pagePost", args=(slug,)))
            elif request.user.is_anonymous():
                comment = CommentAnonymousForm(request.POST, prefix="comment")
                comment = comment.save(commit=False)
                comment.base_post = Post.objects.get(slug=slug)
                comment.key = str(random.random())[2:14]
                comment = comment.save()
                sendCommentConfirmationMail.delay(comment.id)
                messages.info(request, _("Please check your mailbox and confirm your comment."))
                return HttpResponseRedirect(reverse("pagePost", args=(slug,)))
        else:
            messages.error(request,
                           _("Please fill all fields."))
            return HttpResponseRedirect(reverse("pagePost", args=(slug,)))