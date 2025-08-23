from django.shortcuts import render

def home(request):
    return render(request, 'softdesk_support/home.html')
