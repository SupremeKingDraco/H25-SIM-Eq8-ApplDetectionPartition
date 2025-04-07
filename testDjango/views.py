# from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'testDjango/home.html', {})

def about(request):
    return render(request, 'testDjango/about.html', {})

def check(request):
    return render(request, 'testDjango/check.html', {})
def detection(request):
    return render(request, 'testDjango/detection.html', {})