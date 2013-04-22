from models import Category


def contpro_categories(request):
    return {'contpro_categories': Category.objects.all()}
