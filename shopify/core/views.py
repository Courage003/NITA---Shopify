from django.shortcuts import render, redirect
from urllib import request
from django.http import JsonResponse
from django.views import View
from .models import Product, Customers, Cart
from django.db.models import Count
from .forms import CustomerProfileForm,RegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import socket



# Create your views here.
def index(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')

#locals built in function to bring local variables generated to the function
class CategoryView(View):
    def get(self,request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')

        return render(request, 'core/category.html', locals())
    

class CategoryTitle(View):
    def get(self,request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title') #we get all the titles of that category

        return render(request, 'core/category.html', locals())    
    

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"core/productdetail.html", locals())
    

class RegistrationView(View):
    def get(self,request):
        form = RegistrationForm()
        return render(request, 'core/customerregistration.html', locals())

    def post(self,request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Registered Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'core/customerregistration.html', locals())    


class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'core/profile.html', locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            hostel = form.cleaned_data['hostel']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']


            reg = Customers(user=user, name=name, hostel=hostel, mobile=mobile, city=city, state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulations! Profile Saved Successfully")
        else:
            messages.warning(request,"Invalid Input data")
        return render(request, 'core/profile.html', locals())
    

def address(request):
    add = Customers.objects.filter(user=request.user)
    return render(request, 'core/address.html', locals())


class updateAddress(View):
    def get(self,request,pk):
        add = Customers.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)  #advantageous in django
        return render(request,  'core/updateAddress.html', locals())
    

    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customers.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.hostel = form.cleaned_data['hostel']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile Update Successfully")
        else:
            messages.warning(request, "Invalid Input Data")

        return redirect("address")
    

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product_id = product_id.rstrip('/')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40    
    return render(request, 'core/addtocart.html', locals())


class checkout(View):
    def get(self,request):
        user=request.user
        add=Customers.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40    
        return render(request,'core/checkout.html',locals())
    

def plus_cart(request):
    try:
        if request.method == 'GET':
            prod_id = request.GET.get('prod_id')
            
            # Handling the case where multiple cart items might exist
            cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
            
            if cart_items.exists():
                # If multiple items exist, let's just pick the first one or you can decide to merge them
                c = cart_items.first()
                c.quantity += 1
                c.save()

                # Optionally, if you want to handle the case where you might merge quantities:
                for extra_item in cart_items[1:]:
                    c.quantity += extra_item.quantity
                    extra_item.delete()  # Delete the extra items after merging

                c.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'No such cart item found'})
            
            # Calculating the total amount and the overall cart value
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount += value
            
            totalamount = amount + 40  # Assuming 40 is a fixed shipping charge or similar

            # Preparing the response data
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)

    except socket.error as e:
        if isinstance(e, BrokenPipeError):
            # Handle the broken pipe error, or just log it and ignore
            print("Broken pipe error occurred")
            return JsonResponse({'status': 'error', 'message': 'Connection lost with client'})
        else:
            raise



def minus_cart(request):
    try:
        if request.method == 'GET':
            prod_id = request.GET.get('prod_id')
            
            # Handling the case where multiple cart items might exist
            cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
            
            if cart_items.exists():
                # If multiple items exist, let's just pick the first one or you can decide to merge them
                c = cart_items.first()
                if c.quantity > 0:
                    c.quantity -= 1
                    c.save()

                    # Optionally, if you want to handle the case where you might merge quantities:
                    for extra_item in cart_items[1:]:
                        c.quantity += extra_item.quantity
                        extra_item.delete()  # Delete the extra items after merging

                    c.save()
                else:
                    return JsonResponse({'status': 'error', 'message': 'Quantity cannot be less than zero'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No such cart item found'})
            
            # Calculating the total amount and the overall cart value
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount += value
            
            totalamount = amount + 40  # Assuming 40 is a fixed shipping charge or similar

            # Preparing the response data
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)

    except BrokenPipeError:
        # Handle the broken pipe error, or just log it and ignore
        print("Broken pipe error occurred")
        return JsonResponse({'status': 'error', 'message': 'Connection lost with client'})
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred'})
    


def remove_cart(request):
    try:
        if request.method == 'GET':
            prod_id = request.GET.get('prod_id')

            # Find the cart items matching the product and user
            cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
            
            if cart_items.exists():
                # Optionally, handle the case where there might be multiple items
                for item in cart_items:
                    item.delete()  # Remove all cart items for this product
                
                # Recalculate the total amount after removal
                user = request.user
                cart = Cart.objects.filter(user=user)
                amount = 0
                for p in cart:
                    value = p.quantity * p.product.discounted_price
                    amount += value
                
                totalamount = amount + 40  # Assuming 40 is a fixed shipping charge or similar

                # Prepare the response data
                data = {
                    'status': 'success',
                    'message': 'Item removed from cart',
                    'amount': amount,
                    'totalamount': totalamount
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'status': 'error', 'message': 'No such cart item found'})
    
    except BrokenPipeError:
        # Handle the broken pipe error, or just log it and ignore
        print("Broken pipe error occurred")
        return JsonResponse({'status': 'error', 'message': 'Connection lost with client'})
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred'})

