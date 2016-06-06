from django.http import HttpResponse
from django.http import Http404
import sys
import zipfile
import StringIO
import os
from django.contrib.auth.decorators import login_required
from datetime import datetime    


from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django import forms
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from wsgiref.util import FileWrapper

from tagging.models import Tag, TaggedItem

import json
import socket


from .models import Question, QuestionForm, QuestionSearch, Images, Tables

@login_required
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'questions/index.html', context)
	
@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'questions/detail.html', {'question': question})
    
def makeNewFileName(uploadedName, qid, fnum):
    return settings.QUESTIONS_DIRS + "question-" + str(qid) + "-" + str(fnum) + uploadedName[-4:]

    
def handle_uploaded_file(f, fname):
    with open(fname, 'w') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        
@login_required
def add(request):
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            print "postValues:", request.POST.values()
            print "postKeys:", request.POST.keys()
            print "values", request.FILES.values()
            print "keys",request.FILES.keys()
            
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()

            questionid = question.pk
            
            
            #print request.POST.keys()
            
            getDynamicFormElements(request, questionid, question, False)
            
            cleanupTables(question)
            cleanupFigures(question)
            
            return redirect('detail', question.pk)
        else:
            print "form is not valid?"
    else:
        form = QuestionForm()
    return render(request, 'questions/add.html', {'form': form, 'isEdit': False})

@login_required	
def edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        
        print "postValues:", request.POST.values()
        print "postKeys:", request.POST.keys()
        print "values", request.FILES.values()
        print "keys",request.FILES.keys()
            
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()

            questionid = question.pk
            getDynamicFormElements(request, questionid, question, True)
            cleanupTables(question)
            cleanupFigures(question)
            
            return redirect('detail', question.pk)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'questions/add.html', {'form': form, 'isEdit': True})	

#Helper - not called by URL  
def getDynamicFormElements(request, questionid, question, editMode):
    print "Updating dynamic elements..."
    #figNum = 1
    #lookForFigures = True
    
    #note - no id_ for somereason

    maxUploads = getNumElements("figure_", request.FILES.keys())
    print "At most",maxUploads,"uploaded files."
    
    for figNum in range(1, maxUploads + 1):
        figKey = 'figure_' + str(figNum)
        figSKey = 'figuresource_' + str(figNum)
        print "Looking for", figKey
        if figKey in request.FILES:
            fileName = request.FILES[figKey]
            print "A new file was uplaoded, with key: ", fileName
            print request.FILES.keys()
            print "found in FILES:", request.FILES[figKey]
            
            #if the filename is empty, we're not adding anything
            if fileName == '':
                    #figNum = figNum + 1 #we're going to the next iteration, so we had better do this
                    continue
            
            newFileName = makeNewFileName(str(fileName), questionid, figNum)
                    
            handle_uploaded_file(request.FILES[figKey], newFileName)
            
            fSource = request.POST[figSKey]
            #TODO: if image is empty, do not add
            #TODO: if image is the same as before, do not make a new one
            
            existingImage = Images.objects.filter(question=question,num=figNum)
            print "Existing images:",existingImage
            
            #We would normally delete the image associated here, but since we're in this branch
            #of the if statement, a new file was uploaded; it's okay - we'll just use that one instead.
            
                
            if(not existingImage):
                print "Adding a new image."
                i = Images(question=question, image=newFileName, num=figNum, figure_source=fSource)
                i.save()
            else:
                print "Modifying an existing image"
                i = existingImage[0] #Should only ever be one
                i.image = newFileName
                i.figure_source = fSource
                i.save()
        elif figKey in request.POST and editMode:
            #One of the existing images was modified.
            print figKey, "may have been changed."
            
            oldPostKey = "oldfile_" + str(figNum)
            
            fileName = request.POST[oldPostKey]
            print "Which reported the following key", fileName
            
            fSource = request.POST[figSKey]
            
            existingImage = Images.objects.filter(question=question,num=figNum)
            print "Existing images:",existingImage
            

            if(fileName == 'Deleted'):
                fileName = ''
                
                
            if(not existingImage):
                #Should never happen.
                print "Error ocurred; no image found despite it being edited."
            else:
                print "Modifying an existing image"
                i = existingImage[0] #Should only ever be one
                
                if fileName == '':
                    i.delete()
                else:
                    #The only think we could be updating is the source, since there was no key in FILES for this figure.
                    i.figure_source = fSource
                    i.save()            

        #else:
        #    lookForFigures = False
        #figNum = figNum + 1
            
    
    #tabNum = 1
    #lookForTables = True
    #print "post keys:",request.POST.keys()
    maxFigs = getNumElements("ltable_", request.POST.keys())
    #while lookForTables:
    for tabNum in range(1, maxFigs + 1):    
        tabKey = 'ltable_' + str(tabNum)
        if tabKey in request.POST:
            tableSource = request.POST[tabKey]
            print "there was an additional table, with the expected key: ", tableSource
            
            existingTable = Tables.objects.filter(question=question,num=tabNum)
            if not existingTable:
                print "Adding new table."
                
                if not tableSource == 'Table source':
                    t = Tables(question=question, table=tableSource, num=tabNum)
                    t.save()
            else:
                print "This was an old table."
                if tableSource == 'Table source':
                    #Delete the table.
                    t = existingTable[0]
                    t.delete()
                else:
                    t = existingTable[0]
                    t.table = tableSource
                    t.save()
          
            
        #else:
        #    lookForTables = False
        #tabNum = tabNum + 1
    
#Helper, not called by URL directly    
def getNumElements(prefix, set):
    max = 0
    l = len(str(prefix))
    for k in set:
        key = str(k)
        if not key.startswith(prefix):
            continue
        newInt = int(key[l:])
        if newInt > max:
            max = newInt
    return max
    
#Helper, not called by URL directly
def cleanupTables(question):
    tables = Tables.objects.filter(question=question).order_by("num")
    count = Tables.objects.filter(question=question).count()
    
    for i in range(count):
        t = tables[i]
        t.num = min(i+1, t.num)
        t.save()
        
#Helper, not called by URL directly
def cleanupFigures(question):
    images = Images.objects.filter(question=question).order_by("num")
    count = Images.objects.filter(question=question).count()
    
    for i in range(count):
        f = images[i]
        f.num = min(i+1, f.num)
        f.save()        
            

@login_required
def deleteAllQuestions(request):
    if request.user.is_superuser:
        deleteAllQuestionsAndClean()
        return render(request, 'questions/qalldeleted.html')
    else:
        noAccess(request)
            
@login_required
def deleteQuestion(request, question_id):
    if request.user.is_superuser:
        question = get_object_or_404(Question, pk=question_id)
        deleteQuestionAndClean(question)
        removeFromCartHelper(request, question_id)
        return render(request, 'questions/qdeleted.html')
    else:
        noAccess(request)
        
#Helper, not called by URL directly
def deleteQuestionAndClean(question):
    images = Images.objects.filter(question=question)
    for i in images:
        i.delete()
    tables = Tables.objects.filter(question=question)
    for t in tables:
        t.delete()
    
    tags = question.get_tags()
    
    question.delete()
    
    for tag in tags:
        tcount = TaggedItem.objects.get_by_model(Question, tag).count()
        if tcount == 0:
            tag.delete()
    
#Helper, not called by URL directly    
def deleteAllQuestionsAndClean():
    questions = Question.objects.all()
    for q in questions:
        deleteQuestionAndClean(q)

@login_required	
def generateCartOptions(request):
    return render(request, 'questions/cartoptions.html')        
        
@login_required	
def search(request):
    form = QuestionSearch()
    return render(request, 'questions/search.html', {'form': form})

@login_required
def searchresults(request):
    if 'tags' in request.GET:
        searchedtags = request.GET['tags']
        foundquestions = TaggedItem.objects.get_by_model(Question, searchedtags)
        
        context = {'taglist': searchedtags, 'questions':foundquestions}
        
        if "exam_cart" in request.session:
            print("There are questions in the list - search")
            examList = request.session["exam_cart"]
            cart_question_list = Question.objects.filter(id__in=examList)
            context.update({'cart_question_list': cart_question_list})
            
            #filterResultsFlag = request.GET['filterResults']
            #print filterResultsFlag, "is the flag"
            #if filterResultsFlag == "off":
            if 'filterResults' not in request.GET:
                foundquestionsFiltered = foundquestions.exclude(id__in=examList)
                context['questions']=foundquestionsFiltered
            
            print cart_question_list
        else:
            print("The cart is empty")
        
        return render(request, 'questions/searchresults.html', context)
    else:
        return HttpResponse('Please submit a search term.')

@login_required
def ajax(request):
    
    if request.POST.has_key('client_response'):
        x = request.POST['client_response']                  
        y = x                        
        response_dict = {}                                          
        response_dict.update({'server_response': y })
        
        toDeleteString = request.POST['delete_question']
        toDelete = toDeleteString == "true"
        print toDelete, toDeleteString
        
        if toDelete:
            print "Deleting question.."
            removeFromCartHelper(request, x)
        else:
            print "Adding question..."
            addQuestionToCart(request, x)
            print request.session["exam_cart"]
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript') 
    elif request.POST.has_key('add_files'):
        print "getting to add file ajax"
        response_dict = {}                                          
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript') 
    else:
        #TODO: this.
        return render_to_response('questions/searchresults.html', context_instance=RequestContext(request))
   

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
def downloadFigure(request, figure_num, question_id):
    print "want to download figure", figure_num, "for question", question_id
    q = Question.objects.get(id=question_id)
    fig = Images.objects.get(question=q,num=figure_num)
    filename = fig.image.name
    
    print "which has filepath", filename
    wrapper = FileWrapper(file(filename))

    resp = HttpResponse(wrapper, content_type = 'application/force-download')
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % fig.get_fig_name()
    resp['Content-Length'] = os.path.getsize(filename)


    return resp
    
    
@login_required
def store(request, question_id):
    addQuestionToCart(request, question_id)
    return render(request, 'questions/qadded.html')
    
#Helper, not intended to be called by URL directly
def addQuestionToCart(request, question_id):
    if "exam_cart" in request.session:
        cart = request.session["exam_cart"]
        cart.append(question_id)
        request.session["exam_cart"] = cart
    else:
        cart = [question_id]
        request.session["exam_cart"] = cart    
    
@login_required
def removeFromCart(request, question_id):
    removeFromCartHelper(request, question_id)
    return render(request, 'questions/qremoved.html')
    
#Helper, not intended to be called by URL directly
def removeFromCartHelper(request, question_id):
    if "exam_cart" in request.session:
            cart = request.session["exam_cart"]
            if question_id in cart:
                cart = remove_values_from_list(cart, question_id)
                request.session["exam_cart"] = cart
                print("Question was removed - ",cart)
            if len(cart) == 0: 
                del request.session["exam_cart"]
#Helper
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]
   
@login_required
def emptyCart(request):
    if "exam_cart" in request.session:
        del request.session["exam_cart"]
    return render(request, 'questions/cartempty.html')  

@login_required
def generateOptions(request):
    print "POST keys:", request.POST
    
    examName = request.POST['examName']
    
    headerText = request.POST['header_textarea']
    footerText = request.POST['footer_textarea']
    
    request.session['exam_header'] = headerText
    request.session['exam_footer'] = footerText
    request.session['examName'] = examName
    
    order = request.POST['questionlayout']
    
    request.session['exam_order'] = order
    
    if 'images_in_folder' in request.POST.keys():
        request.session['exam_images'] = True 
        
    if 'figures_in_appendix' in request.POST.keys():
        request.session['exam_appendix'] = True

    if 'omitPackages' in request.POST.keys():
        request.session['exam_omit'] = True
    
    request.session['fresh_exam'] = True
    
    return render(request, 'questions/generate.html')   

#Helper, never meant to be called by URL directly:
def noAccess(request):
    return render(request, 'denied.html')

@login_required
def makeExam(request):
    #http://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable
    
    print "In make: ", request.session['exam_order'], request.session['exam_cart']
    
    freshExam = request.session['fresh_exam']
    examName = request.session['examName']
    
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
        
        question = Question.objects.get(id=qid)
        
        question.num_used = question.num_used + 1
        question.last_usded = datetime.now
    
        #TODO: if it does exist, check that it is up to date and use it. If it is not update, generate it again.
        
    request.session['fresh_exam'] = False
        
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
   
    zip_subdir = examName
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