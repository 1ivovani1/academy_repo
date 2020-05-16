from django.shortcuts import render,redirect
from django.http import HttpResponse

from .models import *
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout
# from django.conf import settings
from django.contrib import messages
                
def user_page(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        id = request.GET['id']
        user = CustomUser.objects.get(pk=id)
        ads = Ad.objects.filter(owner=user.username).all()
        length = len(ads)
        
        is_my = (str(request.user.id) == str(id))
        
        return render(request,'user-page.html',{'user':user,'ads':ads,'length':length,'is_my':is_my})


def main(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    ads = Ad.objects.all()

    return render(request,'main.html',{'ads':ads})

def add_ad(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    if request.method == 'GET':
        return render(request,'add_ad.html')

    if request.method == 'POST':
        name = request.POST.get('name','') 
        price = request.POST.get('price','')
        description = request.POST.get('description','')

        if name is '' or price is '' or description is '':
            return HttpResponse('Укажи все нармальна ежжи')
        
        img = request.FILES.get('ad_img','')
        if img is '':
            return HttpResponse('Загрузи пикчу ежжи')
        

        curr_user = request.user
        ad = Ad(name=name,description=description,price=price,image=img,owner=request.user.username,owner_id=curr_user.id)
        ad.save()
        curr_user.ads = ad
        curr_user.save()

        return redirect('/')
        
def logout_page(request):
    logout(request)
    return redirect('/login')

def register_page(request):
    if request.method == 'GET':
        return render(request,'register.html')

    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['user_phone']
        email = request.POST['email']

        if CustomUser.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'Пользователь с таким имененм уже существует!')
            return redirect('/register')

        if username is '' or password is ''or first_name is '' or last_name is '' or phone is '' or email is '':
            messages.add_message(request, messages.ERROR, 'Заполните все поля!')
            return redirect('/register')

    
        user = CustomUser()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            user.avatar = avatar
        user.set_password(password)
        user.save()
        login(request,user)

        return redirect('/')

def search_ads(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    
    query = request.GET.get('query','')
    if query is '':
        return HttpResponse('Неправильно задана строка')

    ads = Ad.objects.filter(name__icontains=query)
    return render(request,'main.html',{'ads':ads})

def login_page(request):
    if request.method == 'GET':
        return render(request,'login.html')

    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.add_message(request, messages.ERROR, 'Пользователь не найден!')
            return redirect('/login')
        else:
            login(request,user)
            return redirect('/')