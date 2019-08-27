from django.shortcuts import render
from questionFilter.models import *
# Create your views here.
def home(request):
    questions = Question.objects.filter(frequency__gte=1)[:50]
    for question in questions:
        question.frequency /= 0.05
    data = {'questions': questions}
    # data = {'question':Question.objects.filter(frequency__gte=1)[:50]}
    return render(request, 'questionFilter/homepage.html', data)

def question_detail(request, slug):
    detail = Question.objects.get(question_slug=slug)
    data = {'detail':detail}
    return render(request, 'questionFilter/question_detail.html', data)
