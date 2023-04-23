from django.shortcuts import render,HttpResponse, redirect
# from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
MERCHANT_KEY = 'kbzk1DSbJiv_O3p5'

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    # print(catprods)
    cats = {item['category'] for item in catprods}
    # print(cats)
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        # print(prod)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1, nSlides), nSlides])
        print(allProds)
    params = {'allProds' : allProds}
    return render(request, 'shop/index.html', params)


def category(request, cat):
    allProds = Product.objects.filter(category=cat)
    params = {'allProds' : allProds}
    return render(request, 'shop/category.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query.lower() in item.desc.lower() or query.lower() in item.product_name.lower() or query.lower() in item.category.lower() or query.lower() in item.subcategory.lower() :
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds' : allProds, "msg" : ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'errmsg':"Please make sure to enter relevant search query"}
        messages.error(request, "Please make sure to enter relevant search query")
        return redirect(request.META['HTTP_REFERER'])
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method=='POST':
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
        messages.success(request,"Thanks for contacting us. We will get back to you soon!")
        return render(request, 'shop/contact.html', {'thank':thank})
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=='POST':
        OrderId = request.POST.get('OrderId','')
        email = request.POST.get('Email','')
        print(OrderId)
        print("Your email id is: "+email)
        try:
            order = Orders.objects.filter(order_id = OrderId)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=OrderId)
                updates = []
                for item in update:
                    updates.append({'text' : item.update_desc, 'time' : item.timestamp})
                    response = json.dumps({"status":"success", "updates":updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"No Item"}')
        except Exception as e:
            return HttpResponse('{"status":"Error"}')

    return render(request, 'shop/tracker.html')

def productView(request, myid):
    product = Product.objects.filter(id=myid)
    # print(product[0].desc)
    # Fetch the product using the id
    return render(request, 'shop/productView.html', {'product':product[0]})

def orders(request):
    if request.user.is_authenticated:
        mailid = request.user.email.strip()
        print("00"+mailid+"00")
        product = Orders.objects.filter(email=mailid.lower()).order_by('-order_id').values()
        params = {'allProds' : product}
        return render(request, 'shop/orders.html', params)
    else:
        return render(request, 'shop/unAuthenticate.html')

def cancelOrder(request, odId):
    if request.user.is_authenticated:
        orderCancelled = Orders.objects.filter(order_id=odId).update(status='Cancelled')
        return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request, 'shop/unAuthenticate.html')

def trackorder(request, odId):
    if request.user.is_authenticated:
        mailid = request.user.email.strip()
        print("00"+mailid+"00")
        product = OrderUpdate.objects.filter(order_id=odId).order_by('timestamp').values()
        order = Orders.objects.filter(order_id=odId).values()
        orderDetails = json.loads(order[0]['items_json'])
        orderDetailsStr = json.dumps(orderDetails)
        params = {'tracking' : product, 'orderDetailsStr': orderDetailsStr, 'status': order[0]['status'], "odId": odId}
        print(order[0]['items_json'])
        return  render(request, 'shop/tracker.html', params)
    else:
        return render(request, 'shop/unAuthenticate.html')


    # print(product[0].desc)
    # Fetch the product using the id

def checkout(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            items_json = request.POST.get('itemsJson', '')
            name = request.POST.get('name','')
            amount = request.POST.get('amount','')
            email = request.POST.get('email','')
            address = request.POST.get('address1','') + "" + request.POST.get('address2', '')
            city = request.POST.get('city','')
            state = request.POST.get('state','')
            zip_code = request.POST.get('zip_code','')
            phone = request.POST.get('phone','')

            order = Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
            order.save()
            update = OrderUpdate(order_id=order.order_id, update_desc='The Order hs been placed')
            update.save()
            # thank = True
            id = str(order.order_id)
            params= { "orderMsg": "Order placed"}
            return render(request, 'shop/checkout.html', params)
        return render(request, 'shop/checkout.html')
    else:
        return render(request, 'shop/unAuthenticate.html')   
    
        

# @csrf_exempt
# def handlerequest(request):
#     # Paytm will send you post request here
#     form = request.POST
#     # print(form)
#     response_dict = {}
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i] 
#     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)

#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             print('order succesfull')
#         else:
#             print('order was not succesfull because'+ response_dict['RESPMSG'])
#     return render(request, 'shop/paymentstatus.html', {'response': response_dict})


# Authentication APIs
def handleSignup(request):
    if request.method == 'POST':
        #Get the post parameters
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

    # Chechk for errorneous inputs
        # User name should be under 10 character
        if len(username) > 15:
            messages.error(request, "Username must be under 15 characters")
            return redirect('ShopHome')

        #Username should be alphanumeric
        if not username.isalnum():
            messages.error(request, "Username should contain letters and numbers")
            return redirect('ShopHome')

        # Passwords should match
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match')
            return redirect('ShopHome')

        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your Mahavir Chemist account has been succesfully created, now you can Login")
        return redirect(request.META['HTTP_REFERER'])

    else:
        return HttpResponse('404 - Not Found')

def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST.get('loginusername')
        loginpassword = request.POST.get('loginpassword')

        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request, user)
            messages.success(request, 'Succesfully Logged In')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, 'Invalid Credentials, Please try again')
            return redirect(request.META['HTTP_REFERER'])
        
    return HttpResponse('404 - Not Found')

def handleLogout(request):
    logout(request)
    messages.success(request, 'Succesfully Logged Out')
    return redirect('ShopHome')