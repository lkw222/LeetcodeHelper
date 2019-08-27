from django.shortcuts import render
from questionFilter.models import *
from django.core.paginator import Paginator
# Create your views here.
def home(request):
    # questions = Question.objects.filter(frequency__gte=1)[:50]
    questions = Question.objects.all().order_by('front_id')[:50]

    for question in questions:
        question.frequency /= 0.05
    limit = 20
    paginator = Paginator(questions, limit)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    data = {'questions': contacts}
    # data = {'question':Question.objects.filter(frequency__gte=1)[:50]}
    return render(request, 'questionFilter/homepage.html', data)


# def sorted_by_frequency(request):



def question_detail(request, slug):
    detail = Question.objects.get(question_slug=slug)
    data = {'detail':detail}
    return render(request, 'questionFilter/question_detail.html', data)
