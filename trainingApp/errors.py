from django.http import HttpResponse


def error404(request):
    return HttpResponse("404 page!")


def error500(request):
    return HttpResponse("500 page!")