from django.http import HttpResponse
from django.http import Http404
import sys


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django import forms
from django.utils import timezone


from .models import Question, QuestionForm


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'questions/index.html', context)
	
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'questions/detail.html', {'question': question})


def add(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()
            return redirect('detail', question.pk)
    else:
        form = QuestionForm()
    return render(request, 'questions/add.html', {'form': form})
	
def edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()
            return redirect('detail', question.pk)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'questions/add.html', {'form': form})	