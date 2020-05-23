from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.core.mail import send_mail,get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail

from .models import *
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib import messages

import random
                
def user_page(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        id = request.GET['id']
        user = CustomUser.objects.get(pk=id)
        ads = Ad.objects.filter(owner=user.username).all()
        length = len(ads)
        
        is_my = (str(request.user.id) == str(id))
        
        all_rates = FeedBack.objects.filter(whom=user.username).all()
        length_of_rates = len(all_rates)
        sum_of_rates = 0
        for i in all_rates:
            sum_of_rates += i.rate

        if length_of_rates == 0:
            average_rate = 0
        else:
            average_rate = round(sum_of_rates/length_of_rates)

        return render(request,'user-page.html',{'user':user,'ads':ads,'length':length,'is_my':is_my,'rate':average_rate,'user_id':id})

    if request.method == 'POST':
        rate = request.POST.get('rate')       
        user_id = request.POST.get('user_id','')
        if user_id is '' or not CustomUser.objects.filter(id=user_id).exists():
            messages.add_message(request, messages.ERROR, 'Пользователя с таким id нет!')
            return redirect('/')

        user = CustomUser.objects.get(pk=user_id)
        new_rate = FeedBack(rate=rate,whom=user)
        new_rate.save()

        return redirect('/user?id=' + str(user.id))

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

        if CustomUser.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'Пользователь с таким email уже существует!')
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

def forgotten_password(request):
    if request.method == 'GET':
        return render(request,'forgotten.html')
    
    if request.method == 'POST':
        email = request.POST.get('email','')
        
        if not CustomUser.objects.filter(email=email).exists(): 
            messages.add_message(request, messages.ERROR, 'Пользователь с таким email нет!')
            return redirect('/reset')
        if email is '':
            messages.add_message(request, messages.ERROR, 'Введите email корректно!')
            return redirect('/reset')

        chars = 'abcdefghjknopqrstuvwxyzABCDEFGHJKMNOPQRSTUVWXYZ1234567890'
        password = ''
        length = 8
        for i in range(length):
            password += random.choice(chars)

        user = CustomUser.objects.filter(email=email).first()

        try:
            connection = get_connection(username="",password='',host='smtp.mail.ru',port=465,use_tls=False,use_ssl=True)
            html_message = render_to_string('email_change.html',{'firstname':user.first_name,'lastname':user.first_name,'password':password})
            plain_message = strip_tags(html_message)
            mail.send_mail('Смена пароля',plain_message,"",[email],html_message=html_message,connection=connection)

            
            user.set_password(password)
            user.save()

            return redirect('/reset')
        except:
            messages.add_message(request, messages.ERROR, 'Произошла неизвестная ошибка на сервере!')
            return redirect('/reset')
