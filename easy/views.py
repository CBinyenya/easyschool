__author__ = 'Monte'
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory
from easy.models import TeacherForm, Teacher, Parent
from django.template import RequestContext
from django.db import IntegrityError

def my_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/easy/login")
    else:
        if request.user.is_staff:
            return HttpResponseRedirect("/admin")
        else:
            return HttpResponse("Your panel is not activated yet")

def signup_view(request):
    if not request.user.is_authenticated():
        return render_to_response("admin1/signup.html", RequestContext(request))
    else:
        if request.user.is_staff:
            return HttpResponseRedirect("/admin")
        else:
            return HttpResponse("Your panel is not activated yet")

def details_view(request):
    user = request.user
    username = request.POST['username']
    account = request.POST['user_account']
    passwd = request.POST['password']
    if account == "teacher":
        request.user = Teacher(username=username)
        form_set = formset_factory(TeacherForm)
    elif account == "parent":
        request.user = Parent(username=username)
        form_set = formset_factory(Parent)
    elif account == "both":
        user1 = Parent(username=username)
        user1.set_password(passwd)
        request.user = Teacher(username=username)
        form_set = formset_factory(Teacher)
    else:
        return HttpResponse("Please select an account type")
    try:
        request.user.set_password(passwd)
        request.user.save()
    except IntegrityError:
        return HttpResponse("This username is not available")
    formset = form_set()
    return render_to_response("admin1/sign_up.html", {'formset':formset}, RequestContext(request))



