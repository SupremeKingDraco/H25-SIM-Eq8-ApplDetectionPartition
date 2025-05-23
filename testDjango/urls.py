from django.urls import path
from  . import views

urlpatterns = [
    path('', views.detection, name='detection'),
    # path('', views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('check/', views.check, name='check'),
    path('bouttonTest/', views.bouttonTest, name='bouttonTest'),

    path('detection-api/', views.detectionApi, name="detectionApi")

]
