#!/usr/bin/env python3.6
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
]