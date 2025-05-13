from django.urls import path
from .views import *

urlpatterns = [
    path('bill_gen/',BillGen.as_view()),
]
