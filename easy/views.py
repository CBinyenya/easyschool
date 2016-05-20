from __future__ import division
__author__ = 'Monte'
import csv
import json
import random
from xlrd import open_workbook
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.forms.formsets import formset_factory
from django.db import IntegrityError
from django.db.models import Q
from django.views.generic.edit import ProcessFormView
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from easy.models import *


def api_login_view(request):
    username = request.POST['username']
    request.user = User(username=username)
    password = request.POST['password']
    HttpResponse(request.user.check_password(raw_password=password))

@login_required(login_url='/easy/login/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/easy/login")

class SignUpView(ProcessFormView):
    """
    Create an account for a new system user e.i. teacher, parent and student
    """
    form_class = TeacherForm
    initial = {'key': "value"}
    template_name = "admin1/signup.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        account = request.POST['user_account']
        passwd1 = request.POST['password1']
        passwd2 = request.POST['password2']

        if passwd1 != passwd2:
            error = "Passwords do not match"
            return render(request, self.template_name, {'errors': error})

        try:
            User.objects.get(username=username)
            form_errors = "This username is not available for use"
            return render(request, self.template_name, {'errors': form_errors})

        except ObjectDoesNotExist:
            request.user.username = username

        if account == "teacher":            
            teacher = Teacher.objects.create_user(username=request.user.username)
            teacher.set_password(passwd1)
            request.user.is_staff = True
            teacher.save()
            group = Group.objects.get(name="Teachers")
            group.user_set.add(teacher)
            group.save()
            return HttpResponseRedirect("/easy/profile/%d" % teacher.id)

        elif account == "parent":
            parent = Parent.objects.create_user(username=request.user.username)
            parent.set_password(passwd1)
            parent.save()
            group = Group.objects.get(name="Parents")
            group.user_set.add(parent)
            group.save()
            logout(request)
            return HttpResponse("Your account has been created. Please download our app from google play to start using"
                                " easy school")

        elif account == "student":
            student = Student.objects.create_user(username=request.user.username)
            student.set_password(passwd1)
            student.save()
            group = Group.objects.get(name="Students")
            group.user_set.add(student)
            group.save()
            logout(request)
            return HttpResponse("Success! your account has been created. Contact your class teacher to upload your"
                                " details")
        elif account == "both":
            return HttpResponse("Teacher parent account is not available at the moment well notify you when its ready"
                                "Please sign in as either a teacher or parent")
        else:
            error = "Please select an account type"
            return render(request, self.template_name, {'errors': error})


def details_view(request):
    username = request.user.username
    try:
        teacher = Teacher.objects.get(username=username)
        new = dict()
        new['username'] = username
        new['email'] = teacher.email
        new['phone'] = teacher.phone
        new['passwd'] = teacher.password
        teacher.delete()
        _formset = formset_factory(TeacherForm)
        formset = _formset(request.POST, request.FILES)
        form = formset[0]
        if form.is_valid():
            form.save()
            obj = Teacher.objects.update_or_create(username="", defaults=new)
            logout(request)
            return HttpResponseRedirect("/easy/login")
        else:
            form = _formset()
            return render(request, "pages/sign_up.html", {'form': form})
    except ObjectDoesNotExist:
        try:
            parent = Parent.objects.get(username=username)
            parent.delete()
            _formset = formset_factory(ParentForm)
            formset = _formset(request.POST, request.FILES)
        except ObjectDoesNotExist:
            try:
                student = Student.objects.get(username=username)
                student.delete()
                _formset = formset_factory(StudentForm)
                formset = _formset(request.POST, request.FILES)
            except ObjectDoesNotExist:
                return HttpResponse("Fatal Error")

    for form in formset:
        if form.is_valid():
            form.save()
            request.user.objects.update_or_create(username="")
        else:
            form = _formset()
            return render(request, "pages/sign_up.html", {'form': form})
    logout(request)
    return HttpResponseRedirect("/easy/login")

def my_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/easy/login")
    else:
        if request.user.is_staff:
            try:
                username = request.user.username
                teacher = Teacher.objects.get(username=username)
                return HttpResponseRedirect("/easy/teacher/%d" % teacher.id)
            except ObjectDoesNotExist:
                return HttpResponseRedirect("/admin")
        else:
            username = request.user.username
            try:
                teacher = Teacher.objects.get(username=username)
                return HttpResponseRedirect("/easy/teacher/%d" % teacher.id)
            except ObjectDoesNotExist:
                try:
                    Student.objects.get(username=username)
                    return HttpResponseRedirect("/easy/student")
                except ObjectDoesNotExist:
                    return HttpResponse("Please download our app from play store to view your child's records")


class SchoolRequestView(TemplateView):
    template_name = "pages/school_request.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SchoolRequestView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        tday = timezone.now()
        year = tday.year
        context = dict()
        context['teacher'] = teacher
        context['full_name'] = full_name
        context['year'] = year
        context['page'] = "tests"
        school = get_school(teacher)

        if school:
            context['school'] = school
            context['message'] = "You are already a teacher at %s. Do you want to change this?" % school.school_name
            context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
            context['num_of_students'] = len(Student.objects.filter(school=school))
            tests = Results.objects.all()
            context['tests'] = tests

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super(SchoolRequestView, self).get_context_data(**kwargs)


@login_required(login_url='/easy/login/')
def teacher_home_page(request, pk=None):
    """
    Redirects to the teacher's dashboard
    """
    context = dict()
    username = request.user.username
    tday = timezone.now()
    year = tday.year
    teacher = Teacher.objects.get(username=str(username))

    positions = list()
    for position in teacher.position.all():
        positions.append(position.name)

    # create the contents needed for the teachers dashboard
    try:
        member = TeacherMembership.objects.get(teacher=teacher)
        context['school'] = member.school
    except TeacherMembership.DoesNotExist:
        if "Head Teacher" not in positions:
            context['error'] = "Please request a school you would like to or are teaching"
            return HttpResponseRedirect("school-update/")

    try:
        context['class'] = Stream.objects.get(class_teacher=teacher)
    except Stream.DoesNotExist:
        pass

    context['teacher'] = teacher
    context['full_name'] = teacher.get_full_name()
    context['year'] = tday.year
    context['subjects'] = teacher.subjects.all()
    context['year'] = year
    context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))

    def initialize_head_teacher():
        try:
            School.objects.get(head=teacher)
            context["head_teacher"] = True
            context["tests"] = get_tests(teacher)
            context['results'] = ResultObjects.objects.filter(supervisor=teacher)
            context['num_of_students'] = len(Student.objects.all())
        except School.DoesNotExist:
            return HttpResponse("Please create a school")
        return context

    def initialize_class_teacher():
        try:
            stream = Stream.objects.get(class_teacher=teacher)
            context['class_teacher'] = teacher.classes.all()
            context['num_of_students'] = len(Student.objects.filter(stream=stream))
        except Stream.DoesNotExist:
            context['num_of_students'] = 0

        context['results'] = ResultObjects.objects.filter(supervisor=teacher)
        context["tests"] = get_tests(teacher)
        return context

    def initialize_subject_teacher():
        context['tests'] = get_tests(teacher)
        context['results'] = ResultObjects.objects.filter(supervisor=teacher)
        return context

    if "Head Teacher" in positions:
        # Initialize Head Teacher functions and attributes
        context = initialize_head_teacher()
        if isinstance(context, HttpResponse):
            return context

    if "Class Teacher" in positions:
        # Initialize Class Teacher functions and attributes
        context = initialize_class_teacher()

    if "Subject Teacher" in positions:
        # Initializing Subject Teacher functions and attributes
        context = initialize_subject_teacher()

    return render(request, "pages/teachers_dashboard.html", context)

def get_tests(teacher):
    today = timezone.now()
    tests = list()
    test_results = list()

    try:
        member = TeacherMembership.objects.get(teacher=teacher)
        if not member.school:
            return list()
        else:
            school = member.school
    except TeacherMembership.DoesNotExist:
        return list()

    for subject in teacher.subjects.all():
        if teacher == school.head:
            test = Exam.objects.filter(school=school)
        else:
            test = Exam.objects.filter(supervisor=teacher, exam_subject=subject)
        max_loop = 0

        # Loop through each test to calculate average results

        for each in test:
            if max_loop > 3:
                break
            results = Results.objects.filter(exam_name=each)

            for result in results:
                avg = average(each)
                if each.date_available > today:
                    try:
                        if teacher == school.head:
                            ResultObjects.objects.create(name=each, subject=subject, results=result, average_marks=avg)
                        else:
                            ResultObjects.objects.create(name=each, subject=subject, results=result, supervisor=teacher,
                                                         average_marks=avg)
                    except IntegrityError:
                        if teacher == school.head:
                            obj = ResultObjects(name=each, subject=subject, results=result)
                        else:
                            obj = ResultObjects(name=each, subject=subject, results=result, supervisor=teacher)
                        obj.average = avg
                        obj.save()
                else:
                    if teacher == school.head:
                            obj = ResultObjects(name=each, subject=subject, results=result)
                    else:
                        obj = ResultObjects(name=each, subject=subject, results=result, supervisor=teacher)

                    if obj.average != avg:
                        obj.average = avg
                        obj.save()

            test_results.append(each.exam_name)
        tests.append(test_results)
    return tests


class TeachersUpdateView(UpdateView):
    model = Teacher
    fields = ["first_name", "last_name", "phone", "email", "gender", "subjects", "position"]
    template_name = "pages/teacher_update_form.html"
    template_name_suffix = '_update_form'

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(TeachersUpdateView, cls).as_view(**initkwargs)
        return login_required(view)

    def get(self, request, *args, **kwargs):
        username = request.user.username
        full_name = request.user.get_full_name()
        teacher = Teacher.objects.get(username=username)
        self.object = Teacher.objects.get(username=username)
        context = self.get_context_data()
        context['teacher'] = teacher
        context['full_name'] = full_name
        return super(TeachersUpdateView, self).render_to_response(context)


class CreateTestView(View):
    tday = timezone.datetime.today()
    year = tday.year

    def get(self, request, *args, **kwargs):
        username = request.user.username
        full_name = request.user.get_full_name()
        teacher = Teacher.objects.get(username=username)
        context = dict()
        context['teacher'] = teacher
        context['full_name'] = full_name
        context['page'] = "create"
        school = get_school(teacher)
        if not school:
            context['error'] = "You don't have any school details. Contact the Head Teacher to include you"
            return render(request, "pages/create.html", context)
        streams = school.stream.all()
        subjects = teacher.subjects.all()

        context['page'] = "create"
        context['subjects'] = subjects
        context['streams'] = streams
        context['school'] = school
        context['year'] = self.year
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['num_of_students'] = len(Student.objects.filter(school=school))

        return render(request, "pages/create.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        f = request.FILES.get('file')
        subject = request.POST.get('subject')
        school = request.POST.get('school')
        streams = request.POST.getlist('streams[]')
        teacher = Teacher.objects.get(username=request.user.username)
        context = dict()
        context['teacher'] = teacher
        context['full_name'] = teacher.get_full_name()
        context['page'] = "create"
        all_subjects = Subject.objects.all()
        if not f:
            context['error'] = "Question file has not been attached"
            return render(request, "pages/create.html", context)
        if not school:
            context['error'] = "You have not registered to any school. Contact admin for help"
            return render(request, "pages/create.html", context)
        school = School.objects.get(school_name=str(school))
        levels = list()
        for level in school.stream.all():
            for each in streams:
                if str(each) == str(level.__str__()):
                    levels.append(level)
        if not levels:
            levels = school.stream.all()
        for each in all_subjects:
            if str(subject) == each.__str__():
                sub = each
                break
        if not sub:
            context['error'] = "Error the subject is not available"
            return render(request, "pages/create.html", context)

        subject = sub.subject_name
        class_level = sub.class_level
        streams = list()
        for level in levels:
            if level.level_name == class_level:
                streams.append(level)

        filename = 'files/uploads/' + name + '.xlsx'
        try:
            obj = ExamUploads.objects.get(exam_name=name)
            obj.excel_file = f
        except ObjectDoesNotExist:
            obj = ExamUploads(exam_name=name, excel_file=f)
        obj.save()
        filename = ExamUploads.objects.get(exam_name=name)
        response = extract_questions(filename.excel_file.url)
        answers = response[1:]
        answers_with_choices = list()
        for ans in answers:
            details = dict()
            letters = ['A', 'B', 'C', 'D']
            choice_answers = list()
            choices = ans[-3:]
            choices.insert(0, ans[-5])
            for evry in enumerate(choices):
                let = random.choice(letters)
                letters.remove(let)
                choice_answers.append((evry[1], let))
            details["question"] = ans[0]
            details['number'] = ans[1]
            details['topic'] = ans[2]
            details['level'] = ans[3]
            details['correct'] = choice_answers[0]
            details['marks'] = ans[5]
            details['choices'] = choice_answers
            answers_with_choices.append(details)
        questions = list()
        for quiz in answers_with_choices:
            try:
                topic = Topic.objects.get(topic_name=quiz['topic'], class_level=class_level, subjects=sub)
            except ObjectDoesNotExist:
                topic = Topic.objects.create(topic_name=quiz['topic'], class_level=class_level, subjects=sub)
            try:
                correct = Answer.objects.create(answer=quiz['correct'][0], letter=quiz['correct'][1],
                                                marks=int(float(quiz['marks'])))
            except:
                context['error'] = "Invalid details for answer: \"%s\". make sure you have specified the marks"\
                                   % quiz['correct'][0]
                return render(request, "pages/create.html", context)
            _answers = list()
            for choice in quiz['choices'][1:]:
                choice = Answer.objects.create(answer=choice[0], letter=choice[1], marks=0)
                _answers.append(choice)
            question = MultipleChoiceQuestion.objects.create(
                question=quiz['question'],
                number=int(float(quiz['number'])),
                class_level=class_level,
                question_subject=sub,
                question_topic=topic,
                level=str(quiz['level'])[0].upper(),
                correct_answer=correct,
            )
            question.choices.add(correct, _answers[0], _answers[1], _answers[2])
            questions.append(question)
        now = timezone.now()
        delta = timezone.timedelta(days=14)
        latter = now + delta
        # hours = models.PositiveSmallIntegerField(choices=HOURS_CHOICES, null=True, blank=True)
        # minutes = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES, null=True, blank=True)

        exam = Exam.objects.create(
            exam_name=name,
            school=school,
            class_level=class_level,
            exam_subject=sub,
            supervisor=teacher,
            date_available=latter,
        )
        for _stream in streams:
            exam.stream.add(_stream)

        for _question in questions:
            exam.questions_ans.add(_question)

        context['message'] = "%s test has been created" % name
        return render(request, "pages/create.html", context)


def create_test_view(request):
    pass

def get_school(teacher):
    try:
        member = TeacherMembership.objects.get(teacher=teacher)
        if not member.school:
            return
        else:
            return member.school
    except TeacherMembership.DoesNotExist:
        return None

def tests_view(request):
    teacher = Teacher.objects.get(username=request.user.username)
    full_name = request.user.get_full_name()
    tday = timezone.now()
    year = tday.year
    context = dict()
    context['teacher'] = teacher
    context['full_name'] = full_name
    context['year'] = year
    context['page'] = "tests"
    school = get_school(teacher)
    if not school:
        context['error'] = "You have not registered to any school. Contact admin for help"
    else:
        context['school'] = school
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['num_of_students'] = len(Student.objects.filter(school=school))
        tests = Results.objects.all()
        context['tests'] = tests

    return render(request, "pages/tests.html", context)

def average(name):
    """
    Calculates the average performance of a class
    """
    try:
        results = Results.objects.filter(exam_name=name)
    except Results.DoesNotExist:
        return 0

    num_of_students = len(results)
    marks = 0

    for result in results:
        marks += result.total_marks
    if marks > 0:
        average = marks/num_of_students
    else:
        average = 0
    return average

class StatisticsPageView(TemplateView):
    template_name = "pages/statistics.html"
    tday = timezone.now()
    year = tday.year

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatisticsPageView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['full_name'] = full_name
        context['teacher'] = teacher
        school = get_school(teacher)
        if school:
            context['num_of_students'] = len(Student.objects.filter(school=school))
        else:
            context['error'] = "You don't have any school details. Contact the Head Teacher to include you"
        return super(StatisticsPageView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(StatisticsPageView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "statistics"
        return context

class ManageStudentsView(TemplateView):
    template_name = "pages/manage.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        streams = list()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()

        for stream in teacher.classes.all():
            streams.append(stream.__str__())

        context['full_name'] = full_name
        context['streams'] = json.dumps(streams)
        context['teacher'] = teacher
        return super(ManageStudentsView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ManageStudentsView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "manage"
        return context


class StudentsPageView(TemplateView):
    template_name = "pages/students.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        students = list()
        tests = list()
        subjects = list()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        _subjects = teacher.subjects.all()
        school = get_school(teacher)
        if school:
            context['num_of_students'] = len(Student.objects.filter(school=school))
        all_students = Student.objects.filter(school=school)
        for subject in _subjects:
            for each in all_students:
                if not subject.class_level or not each.stream:
                    continue
                if subject.class_level == each.stream.level_name:
                    students.append(str(each.get_full_name()))
        for test in Exam.objects.filter(supervisor=teacher):
            tests.append(test.exam_name)
        for sub in _subjects:
            subjects.append(sub.subject_name)
        context['teacher'] = teacher
        context['students'] = json.dumps(list(set(students)))
        context['classes'] = json.dumps(subjects)
        context['tests'] = json.dumps(tests)
        context['num_of_tests'] = len(tests)
        context['full_name'] = full_name
        return super(StudentsPageView, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        student = request.POST.get('student')
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        split = str(student).split(" ")[:2]
        if len(split) < 2:
            fname = split[0]
            sname = ""
        else:
            fname, sname = split
        context['teacher'] = teacher
        context['full_name'] = full_name
        test_name = request.POST.get('test')
        try:
            test = Exam.objects.get(exam_name=test_name)
        except ObjectDoesNotExist:
            context['error'] = "There is no test with the specified name. Have you created any test so far?"
            return super(StudentsPageView, self).render_to_response(context)
        student = Student.objects.filter(Q(first_name__startswith=fname), Q(last_name__startswith=sname))
        if len(student) > 1:
            students = list()
        elif len(student) == 1:
            student = student[0]
        else:
            context["error"] = "No student has been found with the specified name. Give both the first and the last name" \
                               "in that order"
        results = CompletedTests.objects.filter(test=test, student=student)
        context['student'] = student
        context['exam'] = test_name
        context['results'] = results
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        school = get_school(teacher)
        if school:
            context['num_of_students'] = len(Student.objects.filter(school=school))

        return super(StudentsPageView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(StudentsPageView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "students"
        return context


@login_required(login_url='easy/login')
def student_home_page(request):
    tday = timezone.datetime.today()
    year = tday.year
    username = request.user.username
    details = dict()

    try:
        student = Student.objects.get(username=username)
    except ObjectDoesNotExist:
        return HttpResponse("Your account as a student is not available. Please contact your class teacher")

    fullname = student.get_full_name()
    stream = student.stream
    if stream:
        class_level = stream.level_name
    else:
        class_level = 0

    details['fullname'] = fullname
    details['stream'] = stream
    details['year'] = year
    available_tests = list()
    try:
        tests = Exam.objects.filter(class_level=class_level)
        now = timezone.now()
        for test in tests:
            try:
                Results.objects.get(exam_name=test, student_id=student)
                continue
            except ObjectDoesNotExist:
                pass
            available = test.date_available
            if available > now and ([x for x in test.stream.all() if x.stream_name == stream.stream_name]
                                    or not test.stream):
                available_tests.append(test)
        if len(available_tests) < 1:
            info = "There are no available tests at the moment"
        elif len(available_tests) == 1:
            info = "One test available for %s" % stream.stream_name
        else:
            info = "%d tests available for %s" % (len(available_tests), stream.stream_name)

    except ObjectDoesNotExist:
        info = "There are no available tests at the moment"
    details = {
        'tests': available_tests,
        'info': info,
        'fullname': fullname,
        'stream': stream,
        'year': year,
    }
    return render_to_response("pages/units.html", details)


class FormPageView(TemplateView):
    template_name = "pages/formpage.html"
    tday = timezone.datetime.today()
    year = tday.year

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormPageView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        test = request.GET.get('test_code')
        self.exam = Exam.objects.get(exam_name=test)
        context = self.get_context_data()
        context['year'] = self.year
        return super(FormPageView, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        student_name = request.user.username
        try:
            student = Student.objects.get(username=student_name)
        except ObjectDoesNotExist:
            return HttpResponse("Your details are not available")
        test = request.POST['test_code']
        exam = Exam.objects.get(exam_name=test)
        try:
            Results.objects.get(exam_name=exam, student_id=student)
            return HttpResponse("You have already submitted your answers")
        except ObjectDoesNotExist:
            pass
        questions = exam.questions_ans.all()
        txt = ""
        correct = 0
        wrong = 0
        marks = 0
        total_marks = 0
        for quiz in questions:
            answer = request.POST.get(str(quiz.number))
            if answer is not None:
                txt = txt + request.POST.get(str(quiz.number))
                total_marks += quiz.correct_answer.marks                
                if quiz.correct_answer.id == int(answer):                    
                    test = CompletedTests(test=exam, student=student, question=quiz, answer=quiz.correct_answer,
                                          value=True)
                    correct += 1
                    try:
                        marks += quiz.correct_answer.marks
                    except (ValueError, TypeError):
                        marks += 3
                    test.save()
                else:
                    for choice in quiz.choices.all():
                        if choice.id == int(answer):
                            answer = Answer.objects.get(id=choice.id)
                            break
                    if not isinstance(answer, unicode):
                        test = CompletedTests(test=exam, student=student, question=quiz, answer=answer, value=False)
                    wrong += 1
                    test.save()
        results = Results(exam_name=exam, student_id=student, total_marks=marks, out_off=total_marks)
        results.save()
        return HttpResponse("You got %d question(s) correct and %d question(s) wrong" % (correct, wrong))

    def get_context_data(self, **kwargs):
        context = super(FormPageView, self).get_context_data(**kwargs)
        questions = self.exam.questions_ans
        context['exam'] = self.exam
        context['questions'] = questions.all().order_by('number')
        context['year'] = self.year
        return context

def extract_questions(name):
    filename = name
    try:
        wb = open_workbook(filename)
    except IOError, e:
        return False, e
    questions = []
    s = wb.sheets()[0]
    for row in range(s.nrows):
        column_values = []
        for col in range(s.ncols):
            value = s.cell(row, col).value
            column_values.append(str(value))
        questions.append(column_values)
    return questions

def download_student_excel_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Question', 'Number', 'Topic', 'Level', 'Correct Answer', 'Answer 1', 'Answer 2', 'Answer 3'])
    return response


def download_question_excel_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    writer = csv.writer(response)
    writer.writerow(['QUESTION', 'NUMBER', 'TOPIC', 'LEVEL', 'CORRECT ANSWER', 'MARKS', 'ANSWER 1',
                     'ANSWER 2', 'ANSWER 3'])
    return response





