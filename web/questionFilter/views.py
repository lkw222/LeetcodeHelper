from django.shortcuts import render, redirect
from questionFilter.models import *
from questionFilter.forms import *
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

# Create your views here.
def home(request):
    data = {}
    data['companys'] = Company.objects.all().order_by('company_slug')
    data['algorithms'] = Algorithm.objects.all().order_by('algorithm_slug')
    company_selected = request.session.get('company_selected', {})
    data['company_selected'] = company_selected
    algorithm_selected = request.session.get('algorithm_selected', {})
    data['algorithm_selected'] = algorithm_selected
    difficulty_selected = request.session.get('difficulty_selected', {})
    data['difficulty_selected'] = difficulty_selected
    questions = Question.objects.all()

    # Company
    if len(company_selected) > 0:
        # questions = Question.objects.filter(question_slug__in=CompanyTag.objects.filter(company_slug__in=company_selected.keys()).values_list('question_slug', flat=True))
        for cur_company in company_selected:
            questions = questions.filter(companytag__company_slug__company_slug__exact=cur_company)
    # Tag
    if len(algorithm_selected) > 0:
        # questions = questions.filter(question_slug__in=AlgorithmTag.objects.filter(algorithm_slug__in=algorithm_selected.keys()).values_list('question_slug', flat=True))
        for cur_algorithm in algorithm_selected:
            questions = questions.filter(algorithmtag__algorithm_slug__algorithm_slug__exact=cur_algorithm)
    # Difficulty
    if 0 < len(difficulty_selected) < 3:
        questions = questions.filter(difficulty__in=difficulty_selected)

    # Search
    if request.method == 'POST':
        content = request.POST['search_content']
        ids = []
        names = []
        for cur in content.split():
            try:
                ids.append(int(cur))
            except:
                names.append(cur)
        if names != [] and ids != []:
            questions =  questions.filter(Q(name__icontains=' '.join(names)) & Q(front_id__in=ids))
        elif ids != []:
            questions =  questions.filter(Q(front_id__in=ids))
        elif names != []:
            questions =  questions.filter(Q(name__icontains=' '.join(names)))
        else:
            pass
    # Sort
    sort_type = request.session.get('sort_type', 'id')
    if sort_type == 'id':
        questions = questions.order_by('front_id')
    elif sort_type == 'frequency':
        questions = questions.order_by('-frequency')
    elif sort_type == 'AC':
        questions = questions.order_by('-accept_rate')
    elif sort_type == 'name':
        questions = questions.order_by('question_slug')
    data['type'] = sort_type

    for question in questions:
        question.frequency /= 0.05
    limit = 50
    paginator = Paginator(questions, limit)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    data['questions'] = contacts
    return render(request, 'questionFilter/homepage.html', data)


def company_filter(request, company_slug):
    company_selected = request.session.get('company_selected', {})
    if company_slug in company_selected:
        del company_selected[company_slug]
    else:
        company_selected[company_slug] = None

    data = {'company_selected':company_selected}
    request.session['company_selected'] = company_selected
    return HttpResponseRedirect("/")


def algorithm_filter(request, algorithm_slug):
    algorithm_selected = request.session.get('algorithm_selected', {})
    if algorithm_slug in algorithm_selected:
        del algorithm_selected[algorithm_slug]
    else:
        algorithm_selected[algorithm_slug] = None

    data = {'algorithm_selected':algorithm_selected}
    request.session['algorithm_selected'] = algorithm_selected
    return HttpResponseRedirect("/")


def difficulty_filter(request, difficulty):
    difficulty_selected = request.session.get('difficulty_selected', {})
    if difficulty in difficulty_selected:
        del difficulty_selected[difficulty]
    else:
        difficulty_selected[difficulty] = None

    data = {'difficulty_selected':difficulty_selected}
    request.session['difficulty_selected'] = difficulty_selected
    return HttpResponseRedirect("/")

def question_sort(request, sort_type):
    request.session['sort_type'] = sort_type
    return HttpResponseRedirect("/")



def question_detail(request, question_slug):
    detail = Question.objects.get(question_slug=question_slug)
    data = {'detail':detail}
    return render(request, 'questionFilter/question_detail.html', data)
