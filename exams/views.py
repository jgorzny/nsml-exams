from django.shortcuts import get_object_or_404, render
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
    
 #TODO: these    
@login_required
def editExam(request, exam_id):
    return render(request, 'exams/detail.html')
    
@login_required
def searchExams(request):
    return render(request, 'exams/search.html')    
    
@login_required
def deleteAll(request):
    return render(request, 'exams/search.html') 

@login_required
def deleteExam(request, exam_id):
    return render(request, 'exams/search.html')
