from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, UserManager, Poke
from django.db.models import Q, Count
import bcrypt



def index(request):
    return render(request, 'pyexam/index.html')

def register(request):
    name = request.POST['name']
    alias = request.POST['alias']
    email = request.POST['email']
    password = request.POST['password']
    conpass = request.POST['conpass']
    bday = request.POST['bday']
    check = User.objects.register(name, alias, email, password, conpass, bday)
    if check == True:
        pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(name = name, alias = alias, email = email, password = pwhash, bday = bday)
        request.session['current_user'] = user.id
        return redirect('/pokes')
    else:
        for i in range(0, len(check)):
            messages.warning(request, check[i])
        return redirect('/')

def login(request):
    email = request.POST['email']
    password = request.POST['password']
    check = User.objects.login(email, password)
    if check == True:
        user = User.objects.get(email = request.POST['email'])
        request.session['current_user'] = user.id
        return redirect('/pokes')
    else:
        messages.warning(request, check[0])
        return redirect('/')

def logout(request):
    request.session['current_user'] = 0
    return redirect('/')

def pokes(request):
    current_user = User.objects.get(id = request.session['current_user'])
    user = User.objects.all()
    poked_me = User.objects.values('name').annotate(count = Count('name')).filter(poke_to_else__user__id = current_user.id).order_by('-count')
    count_poked_me = User.objects.filter(poke_to_else__user__id = current_user.id).count() #count for how many times people poked me
    not_user = User.objects.filter(~Q(id = current_user.id)).annotate(count = Count('user_to_poke'))
    context = {
                'current_user':current_user,
                'poked_me': poked_me,
                'not_user':not_user,
                'count_poked_me':count_poked_me,
                }
    return render(request, 'pyexam/pokes.html', context)

def poking_action(request, id):
    user = User.objects.get(id = request.session['current_user'])
    poker = User.objects.get(id = id)
    Poke.objects.create(user = poker, poke = user)
    return redirect('/pokes')
