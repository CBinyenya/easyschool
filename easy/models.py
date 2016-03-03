from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from django.contrib.auth.models import User
LEVEL_CHOICES = (
    ('G', "Gold"),
    ('S', "Silver"),
    ('T', "Titanium"),
)
GENDER_CHOICES = (
    ('B', "Boy's School"),
    ('G', "Girl's School"),
    ('M', "Mixed"),
)
GENDER = (
    ('M', "Male"),
    ('F', "Female")
)
PRIVATE_PUBLIC_CHOICE = (
    ('Private', "Private"),
    ('Public', "Public")
)
POSITION_CHOICES = (
    ('HM', "Head Teacher"),
    ('DP', "Deputy teacher"),
    ('SM', "Senior Master"),
    ('EH', "Examination Head"),
    ('AA', "Academic Affairs"),
    ('HOS', "Head of Sciences"),
    ('HOH', "Head of Humanities"),
    ('HOL', "Head of Languages"),
    ('HOM', "Head of Mathematics"),
)
LETTER_CHOICES = (
    ('A', "A"),
    ('B', "B"),
    ('C', "C"),
    ('D', "D"),
)
QUESTION_LEVEL = (
    ('E', "Easy"),
    ('M', "Medium"),
    ('H', "Hard")
)
HOURS_CHOICES = (
    (1, "1 Hour"),
    (2, "2 Hours"),
    (3, "3 Hours"),
)
MINUTES_CHOICES = (
    (15, "15 Minutes"),
    (30, "30 Minutes"),
    (45, "45 Minutes"),
)


class School(models.Model):
    """
    Contains the fields for the student table and defines all the relationships the table has with all other tables.
    The details of this table are to be filled in different levels so as to give a continuous impression of the flow.
    Fields to be field on the first level include:
           school_name, mission, vision, code, logo, email, website, country, county ,city, location, description,
           gender_type, private, head, kindergarten, level
    Fields to be field on the second level include:
            stream, directors
    Fields to be filled on the third level include:
            approved, credit
    Field descriptions:
    1. Gender type - Weather a boy's, girl's or mixed school
    2. private - Weather a private or a public school
    3. Head - Principal or Head Teacher
    4. level - Primary, Secondary, British system
    5. streams - streams of classes in the school, if there is a single stream the word single is used
    6. directors - Board of Directors or a single director for a private school
    7. approved - School is legit as per the ischool company
    8. credit - SMS credit remaining
    """

    school_name = models.CharField(max_length=50)
    mission = models.TextField(max_length=200)
    vision = models.TextField(max_length=200)
    code = models.CharField(max_length=8)
    telephone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=13)
    logo = models.ImageField(null=True, blank=True)
    email = models.EmailField(null=True)
    website = models.URLField(null=True)
    country = models.CharField(max_length=50, default="Kenya")
    county = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50)
    location = models.CharField(max_length=50, null=True)
    description = models.TextField(max_length=500, null=True)
    gender_type = models.CharField(max_length=1, choices=GENDER_CHOICES)
    private = models.CharField(max_length=7, choices=PRIVATE_PUBLIC_CHOICE)
    approved = models.BooleanField(default=False)
    credit = models.PositiveIntegerField(default=0)
    head = models.ForeignKey('Teacher', related_name="skull", null=True)  # temporary null value
    subjects = models.ManyToManyField('Subject', blank=True)
    kindergarten = models.BooleanField(default=False)
    level = models.ForeignKey('SchoolLevel', null=True, blank=True)
    stream = models.ManyToManyField('Stream', blank=True)
    directors = models.ManyToManyField('Director', blank=True)

    '''activity = models.ManyToManyField(
        'Activity',
        null=True,
        on_delete=models.CASCADE
    )
    galary = models.ManyToManyField(
        'Gallery',
        null=True,
        on_delete=models.CASCADE
    )
    events = models.ManyToManyField(
        'Event',
        null=True,
        on_delete=models.CASCADE
    )
    fees_attributes = models.ManyToManyField(
        'FeeStructure',
        null=True,
        on_delete=models.CASCADE
    )
    '''
    no_of_students = models.PositiveIntegerField(null=True, blank=True)
    app_level = models.CharField(max_length=1, choices=LEVEL_CHOICES)

    payed_status = models.BooleanField()

    def __str__(self):
        return self.school_name

    class Meta:
        db_table = "schools"


class Director(User):
    pass

    def __str__(self):
        return self.first_name

    class Meta:
        db_table = "directors"


class Staff(User):
    photo = models.ImageField(null=True, blank=True)
    phone = models.CharField(max_length=13, null=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True)
    school = models.ForeignKey(
        School,
        db_column="school_name",
        related_name="staff",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Teacher(Staff):
    linkdin = models.URLField(null=True)
    subjects = models.ManyToManyField('Subject', blank=True)
    # classes = models.ManyToManyField('Classs', null=True)
    position = models.CharField(max_length=4, choices=POSITION_CHOICES, null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        db_table = "teachers"

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        success_url = "/admin1/login"
        fields = ['photo', 'gender', 'phone', 'position', 'linkdin']


class Subject(models.Model):
    subject_name = models.CharField(max_length=20)
    topics = models.ManyToManyField('Topic', blank=True)
    class_level = models.ForeignKey('ClassLevel', db_column="level_name", null=True)

    def __str__(self):
        return "%s for %s" % (self.subject_name, self.class_level)


class Topic(models.Model):
    topic_name = models.CharField(max_length=50)
    class_level = models.ForeignKey('ClassLevel', db_column="level_name", null=True)
    subjects = models.ForeignKey(Subject, null=True)

    def __str__(self):
        return "%s for %s" % (self.topic_name, self.class_level)

    class Meta:
        db_table = "topics"


class SchoolLevel(models.Model):
    level_name = models.CharField(max_length=20)
    class_level = models.ManyToManyField('ClassLevel')

    def __str__(self):
        return self.level_name

    class Meta:
        db_table = "school_levels"


class ClassLevel(models.Model):
    level_name = models.CharField(max_length=10)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.level_name

    class Meta:
        db_table = "class_levels"


class Stream(models.Model):
    level_name = models.ForeignKey(ClassLevel)
    stream_name = models.CharField(max_length=20)
    class_teacher = models.ForeignKey(Teacher, null=True)

    def __str__(self):
        return "%s %s" % (self.level_name, self.stream_name)

    class Meta:
        db_table = "streams"

        
class Student(User):
    reg_number = models.CharField(max_length=30)
    phone = models.CharField(max_length=13)
    school = models.ForeignKey(School)
    parents = models.ManyToManyField('Parent')
    stream = models.ForeignKey(Stream)

    def __str__(self):
        return self.username

    class Meta:
        pass
        db_table = "students"


class Parent(User):
    phone = models.CharField(max_length=13)

    def __str__(self):
        return "%s %s %s" % (self.username, self.first_name, self.last_name)

    class Meta:
        db_table = "parents"


class Answer(models.Model):
    answer = models.CharField(max_length=30, null=True)
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES)
    image = models.ImageField()


class Question(models.Model):
    question = models.TextField(max_length=200)
    class_level = models.ForeignKey(ClassLevel)
    question_subject = models.ForeignKey(Subject)
    question_topic = models.ForeignKey(Topic, null=True)
    level = models.CharField(max_length=1, choices=QUESTION_LEVEL, null=True)
    correct_answer = models.ForeignKey(Answer)


class MultipleChoiceQeustion(Question):
    choices = models.ManyToManyField(Answer, blank=True)


class Exam(models.Model):
    exam_name = models.CharField(max_length=30)
    class_level = models.ForeignKey(ClassLevel)
    exam_subject = models.ForeignKey(Subject)
    supervisor = models.ForeignKey(Teacher)
    questions_ans = models.ManyToManyField(MultipleChoiceQeustion, blank=True)
    date_available = models.DateTimeField(default=timezone.now)
    hours = models.PositiveSmallIntegerField(choices=HOURS_CHOICES)
    minutes = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES)

    def __str__(self):
        return self.exam_name

    class Meta:
        db_table = "exams"


class Results(models.Model):
    exam_name = models.ForeignKey(Exam)
    student_id = models.ForeignKey(Student)
    total_marks = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.exam_name, self.student_id

    class Meta:
        db_table = "results"

class AdminModel(models.Model):
    pass
