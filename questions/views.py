from django.http import HttpResponse
from django.http import Http404
import sys
import zipfile
import StringIO
import os
from django.contrib.auth.decorators import login_required
from datetime import datetime    

from pylatex import Document, Section, Subsection, Command
from pylatex.utils import  NoEscape

import ast

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from django import forms
from django.utils import timezone
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from wsgiref.util import FileWrapper

from tagging.models import Tag, TaggedItem
from tagging.utils import parse_tag_input

import json
import socket
import shutil
import random


from .models import Question, QuestionForm, QuestionSearch, Images, Tables, Exam, ExamTemplate, Previewcode

#Constant (helper) functions

def cacheMetaExt():
    return "-meta"
    
def cacheQSExt():
    return "-qs"
    
def cacheISExt():
    return "-is"

def cacheFSExt():
    return "-fs"

def cacheASExt():
    return "-as"
    
def getCacheDir(qid):
    return settings.QUESTIONS_DIRS + "q" + str(qid) + "-c" + os.sep
    
def getCartDir(uname):
    return settings.CARTS_DIRS + "cart-" + str(uname) + "" + os.sep    
    
def getImageDir(qid):
    return settings.QUESTIONS_DIRS + "q" + str(qid) + "-i" + os.sep   
   
#Helper
def getQuestions(request):
    publicQuestions = Question.objects.filter(is_public=True) 
    ownedQuestions = Question.objects.filter(initial_author=request.user.username) 
    allQuestions = ownedQuestions | publicQuestions
    return allQuestions
   
@login_required
def index(request):
    allQuestions = getQuestions(request)
    latest_question_list = allQuestions.order_by('pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    
    return render(request, 'questions/index.html', context)
	
#Helper
def getCartFromFile(uname): 
    cartFileName = makeCartFileDir(uname + "-cart.txt", uname) #Ensures that the dir for the file exists
    cfile = open(cartFileName, 'r')
    cartString = cfile.readline()
    
    if cartString == "[]":
        cfile.close()
        return #Do nothing
    else:
        cfile.close()
        return ast.literal_eval(cartString)
    
@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.num_used = getQuestionUseCount(question_id)
    question.save()
    return render(request, 'questions/detail.html', {'question': question})
    
#Helper
def makeNewFileName(uploadedName, qid):
    directory = getImageDir(qid)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + uploadedName

#Helper
def makeCacheFileName(fname, qid):
    directory = getCacheDir(qid)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + fname
    
#Helper
def makeCartFileDir(fname, uname):
    directory = getCartDir(uname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + fname    
    
#Helper    
def handle_uploaded_file(f, fname):
    with open(fname, 'w') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()

#Helper
def makeCachedFiles(qid):
    question = Question.objects.get(id=qid)
    time = question.last_edited
    ftime = time.strftime("%a-%d-%b-%Y-%H-%M-%S")
    
    fnameQS = str(ftime) + cacheQSExt() + ".txt" 
    fnameIS = str(ftime) + cacheISExt() + ".txt"
    fnameFS = str(ftime) + cacheFSExt() + ".txt"
    fnameAS = str(ftime) + cacheASExt() + ".txt"    
    fnameMeta = str(ftime) + cacheMetaExt() + ".txt"
    
    
    fileNameQS = makeCacheFileName(fnameQS, qid)
    fileNameIS = makeCacheFileName(fnameIS, qid)
    fileNameFS = makeCacheFileName(fnameFS, qid)
    fileNameAS = makeCacheFileName(fnameAS, qid)
    
    fileNameMeta = makeCacheFileName(fnameMeta, qid)
    
    writeQSToFile(question, fileNameQS, False)
    writeISToFile(question, fileNameIS, False)
    writeFSToFile(question, fileNameFS, False)
    writeASToFile(question, fileNameAS, False)
    
    writeQMetaToFile(question, fileNameMeta, False)
    
#Helper
def writeQSToFile(question, fileName, append):
    if append:
        mode = 'a'
    else:
        mode = 'w'
        
    f = open(fileName, mode)
    
    f.write("%Question source.\n")
    text  = question.question_text.replace('\r\n', '\n').replace('\r', '\n')
    f.write(text)
    f.write("\n")
    
    f.close()

#Helper
def writeASToFile(question, fileName, append):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    f = open(fileName, mode)
    
    f.write("%Question source.\n")
    text  = question.answer_text.replace('\r\n', '\n').replace('\r', '\n')
    f.write(text)
    f.write("\n")
    
    f.close()
    
#Helper
def writeISToFile(question, fileName, append):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    
    f = open(fileName, mode)
    
    f.write("%Instruction source\n")
    f.write(question.question_instructions)
    f.write("\n")
    
    f.close()

#Helper
def writeFSToFile(question, fileName, append):
    if append:
        mode = 'a'
    else:
        mode = 'w'
        
    f = open(fileName, mode)
    
    figures = question.get_figures()
    for fig in figures:
        f.write("%Figure " + str(fig.num) + "\n")
        f.write(fig.figure_source)
        f.write("\n")
        
    tables = question.get_tables()
    for t in tables:
        f.write("%Table " + str(t.num) + "\n")
        f.write(t.table)
        f.write("\n")
        
    f.close()

#Helper
def writeQMetaToFile(question, fileName, append):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    f = open(fileName, mode)
    
    f.write("%Question publish date: \n")
    f.write("%")
    f.write(str(question.pub_date))
    f.write("\n")
    
    f.write("%Question description: \n")
    f.write("%")
    f.write(question.question_description)
    f.write("\n")
    
    f.write("%Question last edit date: \n")
    f.write("%")
    f.write(str(question.last_edited))
    f.write("\n")

    f.write("%Question number of edits: \n")
    f.write("%")
    f.write(str(question.num_edits))
    f.write("\n")
    
    f.write("%Question contributing authors: \n")
    f.write("%")
    f.write(question.contributing_authors)
    f.write("\n")
    
    f.write("%Question initial author: \n")
    f.write("%")
    f.write(question.initial_author)
    f.write("\n")    

    f.write("%Question notes: \n")
    f.write("%")
    f.write(question.question_notes)
    f.write("\n")  

    f.write("%Question num used: \n")
    f.write("%")
    f.write(str(question.num_used))
    f.write("\n")  
    
    f.write("%Question num used: \n")
    f.write("%")
    f.write(str(question.num_used))
    f.write("\n") 

    f.write("%Question tags: \n")
    f.write("%")
    f.write(str(question.get_tags()))
    f.write("\n") 
    
    f.write("%Question last used on: \n")
    f.write("%")
    f.write(str(question.last_used))
    f.write("\n")    
    
    
    f.close()    
    
#Helper
def updateCachedFiles(qid):
    question = Question.objects.get(id=qid)
    time = question.last_edited
    ftimeNew = time.strftime("%a-%d-%b-%Y-%H-%M-%S")
    fnameNewQS = str(ftimeNew) + cacheQSExt() + ".txt" 
    fnameNewIS = str(ftimeNew) + cacheFSExt() + ".txt"
    fnameNewFS = str(ftimeNew) + cacheISExt() + ".txt"
    fnameNewMeta = str(ftimeNew) + cacheMetaExt() + ".txt"
    fnameNewAS = str(ftimeNew) + cacheASExt() + ".txt"
    
    
    directory = getCacheDir(qid)
    currentFiles = os.listdir(directory)
    
    QSorFSmissing = (not fnameNewQS in currentFiles) or (not fnameNewFS in currentFiles)
    ISorMetaMissing = (not fnameNewIS in currentFiles) or (not fnameNewMeta in currentFiles)
    ASmissing = (not fnameNewAS in currentFiles)
    oneMissing =  QSorFSmissing or ISorMetaMissing or ASmissing
    
    if not oneMissing:
        return
    
    #print "Current files in update", currentFiles
    for f in currentFiles:
        os.remove(directory + f)
    
    if oneMissing:
        makeCachedFiles(qid)
        
 
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
            print "qd:",question.difficulty
            question.pub_date = timezone.now()
            
            question.initial_author = request.user.username
            
            question.save()

            questionid = question.pk
            
            #print request.POST.keys()
            
            getDynamicFormElements(request, questionid, question, False)
            
            cleanupTables(question)
            cleanupFigures(question)
            
            makeCachedFiles(questionid)
            
            return redirect('detail', question.pk)
        else:
            print "form is not valid?"
    else:
        form = QuestionForm()
    return render(request, 'questions/add.html', {'form': form, 'isEdit': False})

#Helper
def getExamsContainingQuestion(qid):
    sw = '['+str(qid)+','
    ew = ','+str(qid)+']'
    con = ','+str(qid)+','
    ex = '[' + str(qid) + ']'
    examList = Exam.objects.filter( Q(questions__startswith=sw) | Q(questions__endswith=ew) | Q(questions__contains=con) | Q(questions__exact=ex) )
    print "exams containing",qid,"are",examList
    return examList
    
#Helper    
def getQuestionUseCount(qid):
    return getExamsContainingQuestion(qid).count()
    
#Helper
def removeQuestionFromExamHelper(qid, e):
    examQuestionsString = e.questions
    if(str(examQuestionsString) == "[]"):
        return
    
    examQuestionList = examQuestionsString.split(',')
    print "exam questions then:",examQuestionList
    out = []
    for le in examQuestionList:
        if '[' in le:
            if ']' in le:
                leFormmated = le[1:-1]
            else:
                leFormmated = le[1:]
        elif ']' in le:
            leFormmated = le[:-1]
        else:
            leFormmated = le
        if int(leFormmated) != int(qid):
            out.append(int(leFormmated))
    e.questions = out
    e.num_edits = e.num_edits + 1
    e.last_edited = timezone.now()
    print "exam questions now:",out
    e.save()
    
    
@login_required	
def removeQuestionFromExams(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user.is_superuser or request.user.username == question.initial_author:
        examList = getExamsContainingQuestion(question_id)
        for e in examList:
            removeQuestionFromExamHelper(question_id, e)
            
        return render(request, 'questions/qremovedfromall.html')
        
    else:
        return noAccess(request)
        
@login_required	
def removeQuestionFromOneExam(request, question_id, exam_id):
    question = get_object_or_404(Question, pk=question_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.user.is_superuser or request.user.username == question.initial_author:
        removeQuestionFromExamHelper(question_id, exam)
            
        examList = getExamsContainingQuestion(question_id)
        return render(request, 'questions/qexams.html', {'exams': examList, 'question': question})        
    else:
        return noAccess(request)        
    
@login_required	
def viewExamsContainingQuestion(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    examList = getExamsContainingQuestion(question_id)
    return render(request, 'questions/qexams.html', {'exams': examList, 'question': question})
 
#Helper
def getPreview(request):
    ownedPreview = Previewcode.objects.filter(preview_author=request.user.username) 
    return ownedPreview 

#Helper #FML
def makeQuestionPDF(question, prev, name):
    if prev != None:
        previewText = prev.previewCode
    else:
        previewText = ""
        
    questionText = question.question_text
    
    #Build the pdf
    doc = Document()
    doc.preamble.append(NoEscape(previewText))
    doc.append(NoEscape(questionText))
    doc.append(NoEscape("EndOfQuestion"))
    folder = 'D:\\Consulting\\NSMLExamBank\\NSMLEB\\questions\\static\\questions\\questionfiles\\pdftemp\\'
    fileName = folder + name
    
    doc.generate_pdf(fileName, clean_tex=True) #appends .pdf to filename.
    fileNameOut = fileName + ".pdf"
    return fileNameOut
 
@login_required	
def renderQuestion(request, question_id): #TODO: this
    question = get_object_or_404(Question, pk=question_id)
    if request.user.username != question.initial_author and not request.user.is_superuser:
        return noAccess(request)
        
    previews = getPreview(request)
    if(len(previews) > 0):
        prev = previews[0]
    else:
        prev = None

    name = 'test'
    fileName = makeQuestionPDF(question, prev, name)
    sURL = static(fileName)
    print(sURL)
    print(fileName)
    goodName = '/static/questions/questionfiles/pdftemp/' + name + '.pdf'
    print("good", goodName)
    return render(request, 'questions/renderquestion.html', {'question': question, 'file': goodName})        
        
    
 
@login_required	
def edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user.username != question.initial_author and not request.user.is_superuser:
        return noAccess(request)
        
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        
        print "postValues:", request.POST.values()
        print "postKeys:", request.POST.keys()
        print "values", request.FILES.values()
        print "keys",request.FILES.keys()
            
        if form.is_valid():
            question = form.save(commit=False)
            question.last_edited = timezone.now()
            question.num_edits = question.num_edits + 1
            question.save()

            questionid = question.pk
            getDynamicFormElements(request, questionid, question, True)
            cleanupTables(question)
            cleanupFigures(question)
            
            return redirect('detail', question.pk)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'questions/add.html', {'form': form, 'isEdit': True})	

@login_required	
def copyQuestion(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.pk = None #make new pk automatically
    question.save() #make the copy
    if question.contributing_authors == 'None yet':
        question.contributing_authors =  question.initial_author
    else:
        question.contributing_authors =  question.contributing_authors + ", " + question.initial_author
    question.initial_author = request.user.username
    question.question_text = "Copy: " + question.question_text 
    question.save()
    
    return redirect('detail', question.pk)
    
    
#Helper - not called by URL  
def getDynamicFormElements(request, questionid, question, editMode):
    print "Updating dynamic elements..."
    #figNum = 1
    #lookForFigures = True
    
    #note - no id_ for somereason

    maxUploads = getNumElements("figure_", request.FILES.keys()) + getNumElements("figure_", request.POST.keys())
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
            
            newFileName = makeNewFileName(str(fileName), questionid)
                    
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
                i = Images(question=question, image=newFileName, num=figNum, figure_source=fSource, short_name=fileName)
                i.save()
            else:
                print "Modifying an existing image"
                i = existingImage[0] #Should only ever be one
                i.image = newFileName
                i.figure_source = fSource
                i.short_name=fileName
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
                    removeImageFile(i)
                    i.delete()
                else:
                    #The only think we could be updating is the source, since there was no key in FILES for this figure.
                    i.figure_source = fSource
                    i.save()            


    #print "post keys:",request.POST.keys()
    maxFigs = getNumElements("ltable_", request.POST.keys())
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
        return noAccess(request)
            
@login_required
def deleteQuestion(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user.is_superuser or (request.user.username == question.initial_author):
        deleteQuestionAndClean(question)
        removeFromCartHelper(request, question_id)
        removeFiles(question_id)
        return render(request, 'questions/qdeleted.html')
    else:
        return noAccess(request)

#Helper
def removeCacheFiles(qid):
    directory = getCacheDir(qid)
    removeDir(directory)
  
#Helper
def removeDir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        
def removeFiles(qid):
    removeCacheFiles(qid)
    removeImageFiles(qid)
        
#Helper
def removeImageFiles(qid):
    directory = getImageDir(qid)
    if os.path.exists(directory):
        shutil.rmtree(directory)
        
#Helper
def removeImageFile(i):
    os.remove(i.get_fig_name())
       
#Helper, not called by URL directly
def deleteQuestionAndClean(question):
    images = Images.objects.filter(question=question)
    for i in images:
        removeImageFile(i)
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
    context = {}
    if "exam_cart" in request.session:
        print("There are questions in the list - search")
        examList = request.session["exam_cart"]
        cart_question_list = Question.objects.filter(id__in=examList)
        userTemplates = ExamTemplate.objects.filter(template_author=request.user.username) 
        context.update({'cart_question_list': cart_question_list})
        context.update({'personaltemplates': userTemplates})
    return render(request, 'questions/cartoptions.html', context)        
        
@login_required	
def search(request):
    form = QuestionSearch()
    tenTags = getTopTenTags()
    print("tt:",tenTags)
    return render(request, 'questions/search.html', {'form': form, 'tags': tenTags})

#Helper
def getTopTenTags():
    tags = Tag.objects.usage_for_model(Question, counts=True)
    tagCounts = [(tag.name, tag.count) for tag in tags]
    tagCounts.sort(key=lambda tup: tup[1])
    if len(tagCounts) > 10:
        topTenPairs = tagCounts[-10]
    else:
        topTenPairs = tagCounts
    topTen = [x[0] for x in topTenPairs]
    print("topten:",topTen)
    return topTen
    
#Helper
def checkAdditionalTags(list, request):
    moreTags = []
    newList = list[:-1].split(",")
    print("keys,",newList,request.GET.keys())
    for t in newList:
        if t in request.GET.keys():
            moreTags.append(str(t))
    return moreTags
      
#Helper
def getAdditionalTags(list):
    moreTags = []
    newList = list.split(",")
    for t in newList:
        moreTags.append(Tag.objects.get(name=str(t).strip()))
    return moreTags  

#Helper
def getAdditionalTagsString(list, request):
    moreTags = ""
    newList = list.split(",")
    print("keys,",newList,request.GET.keys())
    for t in newList:
        if t in request.GET.keys() and len(str(t)) > 0:
            moreTags = moreTags + ", " + str(t)
    return moreTags[2:]   

#Helper    
def getUniqueTags(additionalTagList, searchedTags):
    #split, remove empty entries
    newSearchedListWithSpaces = searchedTags.split(",")
    newSearchedList = filter(None,[x.strip() for x in newSearchedListWithSpaces]) 
    #print newSearchedList,"NSL",[x.strip() for x in newSearchedListWithSpaces]
    
    allTags = additionalTagList + newSearchedList
    allTags = list(set(allTags))
    allTags = ", ".join(allTags)
    return allTags
    
@login_required
def searchresults(request):
    #if 'tags' in request.GET:
    if 'tags' in request.GET:
        searchedtags = request.GET['tags']
        #print "tags??", searchedtags, len(searchedtags)
        
        if 'suggestedtags' in request.GET:
            additionalTagsList = request.GET['suggestedtags']
            #print("atp:",additionalTagsList)
            additionalTags = checkAdditionalTags(additionalTagsList, request)
            #print("at:",additionalTags)
        else:
            additionalTags = None
        
        if len(searchedtags) > 0:
            foundquestions = TaggedItem.objects.get_union_by_model(Question, searchedtags)
            
            
            
            if ',' in searchedtags:
                tagNamesClean = searchedtags[:-2]
            else:
                tagNamesClean = searchedtags
            
            if additionalTags:
                addTagString = getAdditionalTagsString(additionalTagsList, request)
                addTags = getAdditionalTags(addTagString)
                addTagList = [str(y.name) for y in addTags]
                moreQuestions = TaggedItem.objects.get_union_by_model(Question, addTagList)
                
                foundquestions = foundquestions | moreQuestions
                #print addTagList,"this one"

                tagNamesClean = getUniqueTags(addTagList, searchedtags)
            
            
        else:
            foundquestions = Question.objects.all()
            
            if additionalTags:
                addTagString = getAdditionalTagsString(additionalTagsList, request)
                addTags = getAdditionalTags(addTagString)
                #print addTags
                addTagList = [str(y.name) for y in addTags]
                moreQuestions = TaggedItem.objects.get_union_by_model(Question, addTagList)
                                
                #print"mq",  moreQuestions            
                foundquestions = moreQuestions
                
            if additionalTags:
                tagNamesClean = addTagString
            else:
                tagNamesClean = "No tags"
    

    
    difficulties = ""
    
    context = {'taglist': tagNamesClean, 'questions':foundquestions}

    foundquestions = foundquestions.filter(initial_author=request.user.username) | foundquestions.filter(is_public=True)
    
    if 'searchVEasyQuestions' not in request.GET:
        foundquestions = foundquestions.exclude(difficulty=0)
    else:
        print "easy?",request.GET['searchVEasyQuestions']
        difficulties = difficulties + "Easy, "
        
    if 'searchEasyQuestions' not in request.GET:
        foundquestions = foundquestions.exclude(difficulty=1)
    else:
        difficulties = difficulties + "Very Easy, "
        
    if 'searchMedQuestions' not in request.GET:
        foundquestions = foundquestions.exclude(difficulty=2)
    else:
        difficulties = difficulties + "Medium, "

    if 'searchHardQuestions' not in request.GET:
        foundquestions = foundquestions.exclude(difficulty='3')
    else:
        difficulties = difficulties + "Hard, "

    if 'searchVHardQuestions' not in request.GET:
        foundquestions = foundquestions.exclude(difficulty=4)
    else:
        difficulties = difficulties + "Very Hard, "
                
    if 'maxUses' in request.GET:
        if not request.GET['maxUses']:
            print "No max." #Does nothing
        else:
            maxUses = request.GET['maxUses']
            foundquestions.filter(question_description__lte=maxUses)

    if len(difficulties) > 0:
        difficulties = difficulties[:-2]
    context.update({'diffs': difficulties})
    
    if 'searchText' in request.GET:
        sText = request.GET['searchText']
        if len(sText) > 0:
            foundquestions = foundquestions.filter(question_description__contains=sText)
            context.update({'searchedText': sText})
    
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
            print "fqf", foundquestionsFiltered
            context['questions']=foundquestionsFiltered
        
        print cart_question_list
    else:
        print("The cart is empty")
    context['questions'] = foundquestions  

    return render(request, 'questions/searchresults.html', context)
    #else:
    #    return HttpResponse('Please submit a search term.')

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
def tagList(request):
    alltags = Tag.objects.all()
    context = {'tag_list': alltags }
    return render(request, 'questions/taglist.html', context)
    
@login_required
def tagDetail(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'questions/tagdetail.html', {'tag': tag})    

@login_required
def tagRename(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    if 'newTagName' in request.POST:
        newName = request.POST['newTagName']
        if len(newName) > 0:
            conflicts = Tag.objects.filter(name=newName)
            if conflicts.count() > 0:
                return render(request, 'questions/tagfail.html')   
            else:
                tag.name = newName
                tag.save()
                return render(request, 'questions/tagrenamed.html')    
        else:
            return render(request, 'questions/tagfail.html')   
    else:
        return render(request, 'questions/tagfail.html')   
        
    

@login_required
def tagDelete(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    tag.delete()
    return render(request, 'questions/tagdeleted.html', {'tag': tag})    
    
@login_required
def store(request, question_id):
    addQuestionToCart(request, question_id)
    return render(request, 'questions/qadded.html')
    
#Helper, not intended to be called by URL directly
def addQuestionToCart(request, question_id):
    if "exam_cart" in request.session:
        if request.session["exam_cart"]:
            cart = request.session["exam_cart"]
            cart.append(question_id)
            request.session["exam_cart"] = cart
        else:
            cart = [question_id]
            request.session["exam_cart"] = cart  
    else:
        cart = [question_id]
        request.session["exam_cart"] = cart  
    writeCartToFile(request.user.username, cart)
        
    
    
#Helper  
def writeCartToFile(uname, cart):
    cartFileName = makeCartFileDir(uname + "-cart.txt", uname) #Ensures that the dir for the file exists
    wr = open(cartFileName, 'w')
    wr.write(str(cart))
    
@login_required
def removeFromCart(request, question_id):
    print "Removing question " + str(question_id)
    removeFromCartHelper(request, question_id)
    return render(request, 'questions/qremoved.html')
    
#Helper, not intended to be called by URL directly
def removeFromCartHelper(request, question_id):
    print request.session.keys()
    if "exam_cart" in request.session:
            print "A"
            cart = request.session["exam_cart"]
            print str(cart) + " " + question_id
            if question_id in cart:
                print "aaaa"
            if question_id in cart:
                print "B"
                cart = remove_values_from_list(cart, question_id)
                request.session["exam_cart"] = cart
                print("Question was removed - ",cart)
            if len(cart) == 0: 
                del request.session["exam_cart"]
            writeCartToFile(request.user.username, cart)
#Helper
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]
   
@login_required
def emptyCart(request):
    if "exam_cart" in request.session:
        writeCartToFile(request.user.username, [])
        del request.session["exam_cart"]
    return render(request, 'questions/cartempty.html')  

@login_required
def generateOptions(request):
    print "POST keys:", request.POST
    
    examName = request.POST['examName']
    
    if len(examName) == 0:
        examName = "New Exam-" + request.user.username + "-" + str(timezone.now())
    
    examName = examName.replace(':','-')
    
    examInstance = Exam(exam_name=examName)
    examInstance.pub_date=timezone.now()
    examInstance.exam_author=request.user.username  
    
    headerText = request.POST['header_textarea']
    footerText = request.POST['footer_textarea']
    
    examInstance.header = headerText
    examInstance.footer = footerText
    
    examInstance.exam_description = request.POST['description_textarea']
    if 'shareExam' in request.POST.keys():
        examInstance.is_public = True  
    
    examInstance.last_edited = timezone.now()
    examInstance.num_edits = 0
    
    request.session['exam_header'] = headerText
    request.session['exam_footer'] = footerText
    request.session['examName'] = examName
    
    order = request.POST['questionlayout']
    
    if order == "sections":
        examInstance.layout = '0'
        print "X"
        request.session["exam_order"] = "sections"
    else:
        examInstance.layout = '1'
        print "Y"
        request.session["exam_order"] = "together"
    
    print "Cart:",request.session["exam_cart"]
    if 'question_order' in request.POST.keys():
        #print("order found", request.POST['question_order'])
        questionOrderString = request.POST['question_order']
        orderedQuestionList = processOrderingString(questionOrderString)
        #print("OQL:",orderedQuestionList)
        examInstance.questions = orderedQuestionList
        request.session["exam_cart"] = orderedQuestionList
    else:
        examInstance.questions = request.session["exam_cart"]
    
    if 'images_in_folder' in request.POST.keys():
        request.session['exam_images'] = True 
        examInstance.imagesInFolder = True
    else:
        if 'exam_images' in request.session:
            del request.session['exam_images']
        
    if 'figures_in_appendix' in request.POST.keys():
        request.session['exam_appendix'] = True
        examInstance.figuresInAppendix = True
    else:
        if 'exam_appendix' in request.session:
            del request.session['exam_appendix']        

    if 'omitPackages' in request.POST.keys():
        request.session['exam_omit'] = True
        examInstance.omitPackages = True
    else:
        if 'exam_omit' in request.session:
            del request.session['exam_omit']        
        
    if 'inputFiles' in request.POST.keys():
        request.session['qfiles'] = True
        examInstance.inputFiles = True       
    else:
        if 'qfiles' in request.session:
            del request.session['qfiles']    

    #Omit sections options
    if 'omitQuestionSource' in request.POST.keys():
        request.session['omitQuestionSource'] = True
        examInstance.omitQuestionSource = True
    else:
        if 'omitQuestionSource' in request.session:
            del request.session['omitQuestionSource']         

    if 'omitInstructions' in request.POST.keys():
        request.session['omitInstructions'] = True
        examInstance.omitInstructions = True
    else:
        if 'omitInstructions' in request.session:
            del request.session['omitInstructions']    

    if 'omitAnswers' in request.POST.keys():
        request.session['omitAnswers'] = True
        examInstance.omitAnswers = True
    else:
        if 'omitAnswers' in request.session:
            del request.session['omitAnswers']    

    if 'omitFigures' in request.POST.keys():
        request.session['omitFigures'] = True
        examInstance.omitFigures = True
    else:
        if 'omitFigures' in request.session:
            del request.session['omitFigures']   


    if 'omitMeta' in request.POST.keys():
        request.session['omitMeta'] = True
        examInstance.omitMeta = True
    else:
        if 'omitMeta' in request.session:
            del request.session['omitMeta']             
    
    if 'personal_template' in request.POST.keys():
        if not(request.POST['personal_template'] == "none"):
            user_templates = ExamTemplate.objects.filter(template_author=request.user.username) 
            templateInstance = user_templates.get(pk = request.POST['personal_template'])
            print "requested ti:",request.POST['personal_template']
            print "TI iD:", templateInstance.pk
            examInstance.personal_template = templateInstance    
            request.session['personal_template'] = templateInstance.pk
    
    examInstance.save()
    
    request.session['fresh_exam'] = True
    
    return render(request, 'questions/generate.html', {'exam': examInstance})   

#Helper, never meant to be called by URL directly:
def noAccess(request):
    return render(request, 'denied.html')

@login_required
def makeExam(request):
    #http://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable
    print "in make, all session keys: " + str(request.session.keys())
    print "In make: ", request.session['exam_order'], request.session['exam_cart']
    
    freshExam = request.session['fresh_exam']
    examName = request.session['examName']
    
    
    #Make files for each question
    cart = request.session["exam_cart"]
    
    # Files (local path) to put in the .zip
    filenames = []
    
    updateQuestionStats(cart)
    
    order = request.session['exam_order']
    
    if 'qfiles' in request.session:
        includeSepFiles = request.session['qfiles']
    else:
        includeSepFiles = False
    
    if 'personal_template' in request.session:
        print "personal template was usd..."
        user_templates = ExamTemplate.objects.filter(template_author=request.user.username) 
        templateInstance = user_templates.get(pk = request.session['personal_template'])  
        eheader = templateInstance.header
        print "eh:", eheader
        efooter = templateInstance.footer
    else:
        efooter = ""
        eheader = ""
        
    if 'exam_footer' in request.session:
        efooter = efooter + "\n" + request.session['exam_footer']
   

    if 'exam_header' in request.session:
        eheader = eheader + "\n" + request.session['exam_header']      
    
    
    if 'exam_appendix' in request.session:
        eAppendix = request.session['exam_appendix']
    else:
        eAppendix = False   
        
    if 'omitInstructions' in request.session:
        omitInstructions = request.session['omitInstructions']
    else:
        omitInstructions = False

    if 'omitAnswers' in request.session:
        omitAnswers = request.session['omitAnswers']
    else:
        omitAnswers = False

    if 'omitFigures' in request.session:
        omitFigures = request.session['omitFigures']
    else:
        omitFigures = False

    if 'omitQuestionSource' in request.session:
        omitQuestions = request.session['omitQuestionSource']
    else:
        omitQuestions = False      
        
    if 'omitMeta' in request.session:
        omitMeta = request.session['omitMeta']
    else:
        omitMeta = False         
    
    tempDir = "NOTREAL"
    
    if order == "sections":
        (filesToAdd, tempDir) = makeSectionExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta)
        filenames = filenames + filesToAdd
        
    elif order == "together":
        (filesToAdd, tempDir) = makeTogetherExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta)
        filenames = filenames + filesToAdd
        

    
    request.session['fresh_exam'] = False
        
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
   
    zip_subdir = examName
    if len(zip_subdir) == 0:
        zip_subdir = "generated-exam"
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

    #Clean temporary files
    if not tempDir == "NOTREAL":
        removeDir(tempDir)
    
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        
    return resp
    
#Helper
def updateQuestionStats(cart):
    for qid in cart:
        question = Question.objects.get(id=qid)
        
        question.last_used = timezone.now()
        question.save()
        updateCachedFiles(qid)    
        
#Helper
def makeSectionExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta):
    tempDirName = getTempDirName(settings.QUESTIONS_DIRS)
    
    examDir = settings.QUESTIONS_DIRS  + tempDirName + os.sep 
    
    out = []
    
    if not os.path.exists(examDir):
        os.makedirs(examDir)
        
    if not omitInstructions:
        instructionsFile = examDir + examName + "instructions.tex" 
        texOpenEnumerate(instructionsFile)
        out = out + [instructionsFile]
        
    if not omitQuestions:
        questionsFile = examDir + examName + "questions.tex"
        texOpenEnumerate(questionsFile)
        out = out + [questionsFile]
        
    if not omitAnswers:
        answersFile = examDir + examName + "answers.tex"
        texOpenEnumerate(answersFile)
        out = out + [answersFile]
    
    mainFile = examDir + examName + "main.tex"
    
    
    out = out + [mainFile] 
    
    if eAppendix:
        appendixFile = examDir + examName + "appendix.tex"
        out = out + [appendixFile]
    
    for qid in cart:
        question = Question.objects.get(id=qid)

        qDir = getCacheDir(qid)
        
        if includeSepFiles:
            metaCacheFileName = getFilePath(qDir, "-meta")
            qSourceCacheFileName = getFilePath(qDir, "-qs") 
            
            if not omitQuestions:
                out = out + [qDir + metaCacheFileName, qDir + qSourceCacheFileName]
                texInputFile(questionsFile,metaCacheFileName)
                texItem(questionsFile)
                texInputFile(questionsFile,qSourceCacheFileName)
            
            fSourceCacheFileName = getFilePath(qDir, "-fs")
            if not omitFigures:
                if eAppendix:
                    texInputFile(appendixFile,fSourceCacheFileName)
                    out = out + [qDir + fSourceCacheFileName]            
                else:
                    if not omitQuestions:
                        texInputFile(questionsFile,fSourceCacheFileName)
                        out = out + [qDir + fSourceCacheFileName]
        else:
            if not omitQuestions:
                if not omitMeta:
                    writeQMetaToFile(question, questionsFile, True)
                texItem(questionsFile)
                writeQSToFile(question, questionsFile, True)
                
            if not omitFigures:
                if eAppendix:
                    writeFSToFile(question, appendixFile, True)
                else:
                    if not omitQuestions:
                        writeFSToFile(question, questionsFile, True)
        
        if includeSepFiles:
            aSourceCacheFileName = getFilePath(qDir, "-as")
            
            if not omitAnswers:
                out = out + [qDir + aSourceCacheFileName]
                texItem(answersFile)
                texInputFile(answersFile,aSourceCacheFileName)
        else:
            if not omitAnswers:
                texItem(answersFile)
                writeASToFile(question, answersFile, True)
        
        if includeSepFiles:
            iSourceCacheFileName = getFilePath(qDir, "-is")
            if not omitInstructions:
                out = out + [qDir + iSourceCacheFileName]
                texItem(instructionsFile)
                texInputFile(instructionsFile,iSourceCacheFileName)        
        else:
            if not omitInstructions:
                texItem(instructionsFile)
                writeISToFile(question, instructionsFile, True)
        
        if not omitFigures:
            out = out + getImageFiles(qid)
        
    if not omitInstructions:        
        texCloseEnumerate(instructionsFile)
    if not omitQuestions:
        texCloseEnumerate(questionsFile)
    if not omitAnswers:
        texCloseEnumerate(answersFile)
    
    texDocHeader(mainFile)
    texText(mainFile,eheader)
    if not omitInstructions:
        texSection(mainFile, str("Instructions"))
        texInputFile(mainFile, str(examName) + "instructions.tex")
    if not omitQuestions:
        texSection(mainFile, str("Questions"))
        texInputFile(mainFile, str(examName) + "questions.tex")
    if not omitAnswers:
        texSection(mainFile, str("Answers"))
        texInputFile(mainFile, str(examName) + "answers.tex")
    texText(mainFile,efooter)
    
    if eAppendix:
        texSection(mainFile, str("Appendix"))
        texInputFile(mainFile, str(examName) + "appendix.tex")
    
    texDocClose(mainFile)
    return (out, examDir)

#Helper
def getFilePath(qDir, substring):
    cachedFiles = os.listdir(qDir)
    for f in cachedFiles:
        if substring in f:
            return f
    #TODO: handle errors?
    
def getImageFiles(qid):
    imagesDir = getImageDir(qid)
    out = []
    if os.path.exists(imagesDir):
        cachedFiles = os.listdir(imagesDir)
        for f in cachedFiles:
            out = out + [imagesDir + str(f)]
    return out
    
    
#Helper
def texText(filename, text):
    f = open(filename, 'a')
    f.write("\n")
    f.write(str(text))
    f.write("\n")
    f.close()    
    
#Helper
def texItem(filename):
    f = open(filename, 'a')
    f.write("\\item")
    f.close()
    
#Helper
def texOpenEnumerate(filename):
    f = open(filename, 'a')
    f.write("\\begin{enumerate}\n")
    f.close()
    
#Helper
def texCloseEnumerate(filename):
    f = open(filename, 'a')
    f.write("\\end{enumerate}\n")
    f.close()    
    
#Helper 
def texDocHeader(filename):
    f = open(filename, 'a')
    f.write("\\documentclass[11pt]{article} \n")
    f.write("\\begin{document}\n")
    f.close() 

#Helper
def texDocClose(filename):    
    f = open(filename, 'a')
    f.write("\\end{document}\n")
    f.close()
    
#Helper
def texInputFile(filename, input):    
    f = open(filename, 'a')
    f.write("\\input{")
    f.write(str(input))
    f.write("}\n")
    f.close()

#Helper
def texSection(filename, section):    
    f = open(filename, 'a')
    f.write("\\section{" + str(section) + "}\n")
    f.close()     
    
#Helper
def getTempDirName(base):
    #TODO Better way of doing this?
    noise = random.randint(1,1000000)
    out = "temp" + str(noise)
    while os.path.exists(base + out):
        noise = random.randint(1,1000000)
        out = "temp" + str(noise)
    return out
    
#Helper  
def makeTogetherExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta):
    
    tempDirName = getTempDirName(settings.QUESTIONS_DIRS)
    
    examDir = settings.QUESTIONS_DIRS  + tempDirName + os.sep 
    if not os.path.exists(examDir):
        os.makedirs(examDir)

    mainFile = examDir + examName + "main.tex"
    
    texDocHeader(mainFile)
    texText(mainFile,eheader)
    
    out = [mainFile]
    
    if eAppendix:
        appendixFile = examDir + examName + "appendix.tex"
        out = out + [appendixFile]
    
    for qid in cart:
        question = Question.objects.get(id=qid)
       
        qDir = getCacheDir(qid)
        
        if not omitQuestions:
            texSection(mainFile, str("Question ") + str(qid) )

        
        if includeSepFiles:
            metaCacheFileName = getFilePath(qDir, "-meta")
            qSourceCacheFileName = getFilePath(qDir, "-qs") 
            if not omitQuestions:
                out = out + [qDir + metaCacheFileName, qDir + qSourceCacheFileName]
                if not omitMeta:
                    texInputFile(mainFile,metaCacheFileName)
                texInputFile(mainFile,qSourceCacheFileName)
            
            fSourceCacheFileName = getFilePath(qDir, "-fs")
            
            if not omitFigures:
                if eAppendix:
                    texInputFile(appendixFile,fSourceCacheFileName)
                    out = out + [qDir + fSourceCacheFileName]            
                else:
                    texInputFile(mainFile,fSourceCacheFileName)
                    out = out + [qDir + fSourceCacheFileName]
        else:
            if not omitMeta:
                writeQMetaToFile(question, mainFile, True)
            if not omitQuestions:
                writeQSToFile(question, mainFile, True)
                
            if not omitFigures:
                if eAppendix:
                    writeFSToFile(question, appendixFile, True)
                else:
                    writeFSToFile(question, mainFile, True)
        
        if not omitAnswers:
            if includeSepFiles:
                aSourceCacheFileName = getFilePath(qDir, "-as")
                out = out + [qDir + aSourceCacheFileName]
                texInputFile(mainFile,aSourceCacheFileName)
            else:
                writeASToFile(question, mainFile, True)
        
        if not omitInstructions:
            if includeSepFiles:
                iSourceCacheFileName = getFilePath(qDir, "-is")
                out = out + [qDir + iSourceCacheFileName]
                texInputFile(mainFile,iSourceCacheFileName)        
            else:
                writeISToFile(question, mainFile, True)
        
        if not omitFigures:
            out = out + getImageFiles(qid)
        
    


    texText(mainFile,efooter)
    
    if eAppendix:
        texSection(mainFile, str("Appendix"))
        texInputFile(mainFile, str(examName) + "appendix.tex")
    
    texDocClose(mainFile)
    return (out, examDir)
        
            
#Helper, not intended to be called directly        
def processOrderingString(orderString):
    print("OS:",orderString)
    if "," not in str(orderString):
        #User did not modify order.
        #example string: question[]=146&question[]=144
        questionList = orderString.split('&')
        questionList = [getQNum(s) for s in questionList]
        print("returning",questionList)
        return questionList
    else:
        #User moved (and therefore updated the string)
        lastCommaRemoved = orderString[:-1]
        questionList = lastCommaRemoved.split(',')
        questionList = [int(i) for i in questionList] #make them all ints
        print("returning",questionList)        
        return questionList    
        
def getQNum(s):
    if "cquestion" in s:
        return int(s[12:])
    else:
        return int(s[11:])
