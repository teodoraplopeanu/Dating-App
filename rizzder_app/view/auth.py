from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from ..serializer import user_registration_serializer
from rest_framework.response import Response
from ..models import User
import logging

logger = logging.getLogger(__name__)

def about(request):
    return render(request, "about.html", {})

def signup(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        if User.get(request.POST['username']) is not None:
            return HttpResponse("User is already created!")
        cred = form.save()

        user = User.objects.create(username=request.POST['username'], birth_date=request.POST['birthday'], credential=cred)
        user.save()
        ### TODO add all user's data and save it
        return redirect('login')
    return render(request, 'registration/signup.html', {'form': form})


def login(request):
    return render(request, 'registration/login.html')


def loginRedirect(request):
    return redirect("home")


class user_registration(APIView):
    def post(self, request):
        serializer = user_registration_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'user': user.username, 'data': 'Registration successful'})
        return Response(serializer.errors)

