from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


import questions.models

import sys
import zipfile
import StringIO
import os

from questions.views import makeSectionExam, makeTogetherExam, removeDir

#Helper
def getExams(request):
    publicExams = questions.models.Exam.objects.filter(is_public=True) 
    ownedExams = questions.models.Exam.objects.filter(exam_author=request.user.username) 
    allExams = ownedExams | publicExams
    return allExams

@login_required
def recentExams(request):
    allExams = getExams(request)
    latestExamlist = allExams.order_by('-pub_date')[:5]
    context = {'latest_exam_list': latestExamlist}
    return render(request, 'exams/recent.html', context)
    

   
@login_required
def viewExam(request, exam_id):
    exam = get_object_or_404(questions.models.Exam, pk=exam_id)
    print "view Exam request",exam.questions
    
    examQuestions = getExamQuestions(exam.questions[1:-1])
    return render(request, 'exams/detail.html', {'exam': exam, 'questions': examQuestions}) 

#Helper
def getExamQuestions(cart):
    out = []
    list = cart.split(",")
    for qid in list:
        question = questions.models.Question.objects.get(id=qid)
        out.append(question)
    return out
    
#Helper
def makeIntList(cart):
    out = []
    list = cart.split(",")
    for qid in list:
        out.append(int(qid))
    return out    
      
    
@login_required
def deleteAll(request):
    exams = questions.models.Exam.objects.all()
    for e in exams:
        e.delete()
    return render(request, 'exams/ealldeleted.html')   
    
@login_required
def deleteExam(request, exam_id):
    exam = get_object_or_404(questions.models.Exam, pk=exam_id)
    exam.delete()
    return render(request, 'exams/edeleted.html')    
    
@login_required
def editExam(request, exam_id):
    exam = get_object_or_404(questions.models.Exam, pk=exam_id)
    examQuestionList = getExamQuestions(exam.questions[1:-1])
    return render(request, 'exams/editexam.html', {'exam': exam, 'exam_question_list': examQuestionList})

@login_required
def downloadExam(request, exam_id): 
    exam = get_object_or_404(questions.models.Exam, pk=exam_id)

    examName = exam.exam_name.replace(':','-')
      
    #Make files for each question
    cart = makeIntList(exam.questions[1:-1])
    
    # Files (local path) to put in the .zip
    filenames = []
    
    #this is really layout
    order = exam.layout
    
    includeSepFiles = exam.inputFiles
        
    efooter = exam.footer
    eheader = exam.header       
    
    eAppendix = exam.figuresInAppendix
 
    omitInstructions = exam.omitInstructions
    omitAnswers = exam.omitAnswers
    omitFigures = exam.omitFigures
    omitQuestions = exam.omitQuestionSource
    omitMeta = exam.omitMeta    
            
    tempDir = "NOTREAL"
    
    if order == '0':
        (filesToAdd, tempDir) = makeSectionExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta)
        filenames = filenames + filesToAdd
        
    elif order == '1':
        (filesToAdd, tempDir) = makeTogetherExam(cart, includeSepFiles, examName, eheader, efooter, eAppendix, omitQuestions, omitAnswers, omitInstructions, omitFigures, omitMeta)
        filenames = filenames + filesToAdd
            
        
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
    
#TODO: these    
@login_required
def updateExam(request, exam_id):    
    return render(request, 'exams/search.html')    

    
@login_required
def searchExams(request):
    return render(request, 'exams/search.html')    
    


