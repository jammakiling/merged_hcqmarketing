from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404
from django.urls import reverse
from .models import Index


# Create your views here.

def index(request):
    return render(request, 'index.html', {
        'indexes':Index.objects.all().order_by('id')
    })

