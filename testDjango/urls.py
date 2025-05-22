from django.urls import path
from  . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('check/', views.check, name='check'),
    path('detection/', views.detection, name='detection'),
    path('bouttonTest/', views.bouttonTest, name='bouttonTest'),

    path('detection-api/', views.detectionApi, name="detectionApi")

]
