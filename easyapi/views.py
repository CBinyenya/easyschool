from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from easy.serializers import StudentSerializer
from easy.models import *

@api_view(['GET', 'PUT', 'POST'])
def api_login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            student = Student.objects.get(username=username)
            tests = Exam.objects.filter(class_level=student.stream.level_name)
            available_tests = list()
            if tests:
                now = timezone.now()
                for test in tests:
                    try:
                        Results.objects.get(exam_name=test, student_id=student)
                        continue
                    except ObjectDoesNotExist:
                        pass
                    available = test.date_available
                    if available > now and ([x for x in test.stream.all() if x.stream_name == student.stream.stream_name]
                                            or not test.stream):
                        available_tests.append(test)

        except Student.DoesNotExist:
            try:
                user = Parent.objects.get(username=username)

            except Parent.DoesNotExist:
                try:
                    user = Teacher.objects.get(username=username)
                except Teacher.DoesNotExist:
                    data = {'error': "Please contact your school for registration help"}

        serialize = StudentSerializer(student)
        return Response(serialize.data)