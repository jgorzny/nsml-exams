from django.http import HttpResponse
from django.http import Http404
import sys
from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django import forms
from django.utils import timezone


from .models import Question, QuestionForm

@login_required
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'questions/index.html', context)
	
@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'questions/detail.html', {'question': question})

@login_required
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

@login_required	
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
	
	
@login_required
def cart(request):
    if "exam_cart" in request.session:
        print("There are questions in the list")
        examList = request.session["exam_cart"]
        cart_question_list = Question.objects.filter(id__in=examList)
        context = {'cart_question_list': cart_question_list}
    else:
        print("The cart is empty")
        context = {}
    
    
    return render(request, 'questions/cart.html', context)
    
@login_required
def store(request, question_id):
    print("Store request clicked")
    if "exam_cart" in request.session:
        cart = request.session["exam_cart"]
        cart.append(question_id)
        request.session["exam_cart"] = cart
    else:
        cart = [question_id]
        request.session["exam_cart"] = cart
    return render(request, 'questions/qadded.html')
    
@login_required
def removeFromCart(request, question_id):
    if "exam_cart" in request.session:
        cart = request.session["exam_cart"]
        cart.remove(question_id)
        request.session["exam_cart"] = cart
        print("Question was removed - ",cart)
    return render(request, 'questions/qremoved.html')
    
@login_required
def emptyCart(request):
    if "exam_cart" in request.session:
        del request.session["exam_cart"]
    return render(request, 'questions/cartempty.html')    