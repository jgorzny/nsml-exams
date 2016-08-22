from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from questions.views import getCartFromFile

@login_required
def index(request):
    cart = getCartFromFile(request.user.username)
    request.session["exam_cart"] = cart
    print "NEW CART: " + str(cart)
    
    return render(request, 'home/index.html')