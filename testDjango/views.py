# from django.http import HttpResponse
# from myproject.myproject.cleanProject import process_video_and_generate_midi
from sqlite3.dbapi2 import paramstyle

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from myproject.cleanProject import process_video_and_generate_midi


# Create your views here.
def home(request):
    return render(request, 'testDjango/home.html', {})

def about(request):
    return render(request, 'testDjango/about.html', {})

def check(request):
    return render(request, 'testDjango/check.html', {})
def detection(request):
    return render(request, 'testDjango/detection.html', {})
def bouttonTest(request):
    return render(request, 'testDjango/bouttonTest.html', {})

@csrf_exempt
def detectionApi(request):
    if request.method != 'POST':
        return JsonResponse({"msg": "Mauvais type d'appel."})


    print(request.body)

    data = json.loads(request.body)
    print(data)

    nomChanson = data["userInput"]
    params = data["parsedDynamicInputs"]
    selectedTreatment = data["selectedTreatment"]

    for i in range(len(params)):
        params[i] = int(params[i])

    if (selectedTreatment == "image"):
        process_video_and_generate_midi(nomChanson, params[0], params[1], params[2], params[3])


    return JsonResponse({"msg": "Detection API a été appelé."})
