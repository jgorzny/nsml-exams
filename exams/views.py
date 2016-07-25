from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import questions.models

#Helper
def getExams(request):
    publicExams = questions.models.Exam.objects.filter(is_public=True) 
    ownedExams = questions.models.Exam.objects.filter(exam_author=request.user.username) 
    allExams = ownedExams | publicExams
    return allExams

@login_required
def recentExams(request):
    allExams = getExams(request)
    latestExamlist = allExams.order_by('pub_date')[:5]
    context = {'latest_question_list': latestExamlist}
    return render(request, 'exams/recent.html', context)
    
#TODO: these    
@login_required
def viewExam(request, exam_id):
    return render(request, 'exams/search.html') 
    
@login_required
def searchExams(request):
    return render(request, 'exams/search.html')    
    
@login_required
def deleteAll(request):
    return render(request, 'exams/search.html')  
