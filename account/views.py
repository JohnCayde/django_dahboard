from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
#create your view here
from .models import *
from .forms import orderForm, CreateUserForm
from .filter import OrderFilter

# Create your views here.
def loginPages(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username/Password incorrect')

    context ={}
    return render(request, 'accounts/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')


    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')
    context = {'form':form}
    return render(request, 'accounts/register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()


    total_customer = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    content = {'orders': orders, 'customers':customers, 'total_orders': total_orders, 'delivered':delivered, 'pending':pending}

    return render(request, 'accounts/dashboard.html', content)

@login_required(login_url='login')
def product(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products':products})

@login_required(login_url='login')
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myfilter = OrderFilter(request.GET, queryset=orders)
    orders = myfilter.qs

    context = {'customer':customer, 'orders':orders, 'total_orders':total_orders, 'myfilter':myfilter}
    return render(request, 'accounts/customers.html', context)

@login_required(login_url='login')
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    #form = orderForm(initial={'customer':customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        #print('Printing POST:', request.POST)
        #form = orderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset':formset}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = orderForm(instance=order)
    if request.method == 'POST':
            #print('Printing POST:', request.POST)
            form = orderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('/')

    context = {'form':form}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'item':order}
    return render(request, 'accounts/delete.html', context)