from django.http import HttpResponse
from django.http import Http404
import sys
import zipfile
import StringIO
import os
from django.contrib.auth.decorators import login_required


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django import forms
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings



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

@login_required
def generateOptions(request):
    return render(request, 'questions/generate.html')   

@login_required
def makeExam(request):
    #http://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable
    
    #Make files for each question
    cart = request.session["exam_cart"]
    
    # Files (local path) to put in the .zip
    filenames = []
    for qid in cart:
    
        #if the file does not already exist, make it
        filename = settings.QUESTIONS_DIRS + "question" + qid + ".txt"
        filenames.append(filename)
        f = open(filename, 'w')
        f.write("Testing\n")
     
        #TODO: if it does exist, check that it is up to date and use it. If it is not update, generate it again.
        
        
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # TODO: Set this to something better
    zip_subdir = "Exam"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp