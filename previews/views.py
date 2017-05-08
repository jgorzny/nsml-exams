from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import questions.models
#import questions.models.Previewcode


def getPreview(request):
    ownedPreview = questions.models.Previewcode.objects.filter(preview_author=request.user.username) 
    return ownedPreview

@login_required
def previewUpdate(request):
    
    print("request post keys", request.POST.keys())
    print("request post vals", request.POST.values())
    
    if 'preview_textarea' in request.POST.keys():
        
        code = request.POST['preview_textarea']
        print("code? ",code)
        
        deleteAll(request)
        prev = questions.models.Previewcode(previewCode = code, preview_author=request.user.username)
        prev.save()

    
    ownedPrev = getPreview(request)
    context = {'preview': ownedPrev[0]} #Was just added, so should always exist.
    return render(request, 'previews/viewpreview.html', context)
    
   
    
@login_required
def previewCodeEdit(request):
    ownedPrev = getPreview(request)
    if (len(ownedPrev) == 0):
        #No preview yet
        return render(request, 'previews/editpreview.html')    
    else:
        context = {'preview': ownedPrev[0]}
        return render(request, 'previews/editpreview.html', context) 
        
@login_required
def deleteAll(request): #helper
    ownedPrev = getPreview(request)
    prevs = ownedPrev
    for p in prevs:
        p.delete()            
        
@login_required
def previewCodeClear(request):
    deleteAll(request)
    return render(request, 'previews/viewpreview.html') #TODO this

@login_required
def previewCodeView(request):    
    ownedPrev = getPreview(request)
    if (len(ownedPrev) == 0):
        #No preview yet
        return render(request, 'previews/viewpreview.html')    
    else:
        context = {'preview': ownedPrev[0]}
        return render(request, 'previews/viewpreview.html', context)    