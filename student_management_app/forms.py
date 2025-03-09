from django import forms 
from django.forms import Form
from student_management_app.models import Courses, SessionYearModel

class DateInput(forms.DateInput):
    input_type = "date"

class AddStudentForm(forms.Form):
    # Basic User Information
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    # Personal Information
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
    )

    SECOND_LANGUAGE_CHOICES = (
        ('', 'Select Second Language'),  # Empty default option
        ('HI', 'Hindi'),
        ('ML', 'Malayalam'),
    )

    RELIGION_CHOICES = (
        ('', 'Select Religion'),
        ('Hindu', 'Hindu'),
        ('Muslim', 'Muslim'),
        ('Christian', 'Christian'),
        ('Sikh', 'Sikh'),
        ('Buddhist', 'Buddhist'),
        ('Jain', 'Jain'),
        ('Other', 'Other'),
    )

    CASTE_CHOICES = (
        ('', 'Select Caste'),
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('Other', 'Other'),
    )

    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, widget=forms.Select(attrs={"class":"form-control"}))
    date_of_birth = forms.DateField(label="Date of Birth", widget=forms.DateInput(attrs={"class":"form-control", "type":"date"}))
    blood_group = forms.ChoiceField(label="Blood Group", choices=BLOOD_GROUP_CHOICES, required=False, widget=forms.Select(attrs={"class":"form-control"}))
    phone_number = forms.CharField(label="Phone Number", max_length=15, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", widget=forms.Textarea(attrs={"class":"form-control", "rows":3}))
    religion = forms.ChoiceField(
        label="Religion",
        choices=RELIGION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"})
    )
    
    caste = forms.ChoiceField(
        label="Caste",
        choices=CASTE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"})
    )

    # Academic Information
    admission_number = forms.CharField(label="Admission Number", max_length=50, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    roll_number = forms.CharField(label="Roll Number", max_length=50, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    course_id = forms.ChoiceField(label="Course", widget=forms.Select(attrs={"class":"form-control"}))
    second_language = forms.ChoiceField(
        label="Second Language",
        choices=SECOND_LANGUAGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Select Second Language"
        })
    )
    session_year_id = forms.ChoiceField(label="Session Year", widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Picture", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    # Parent/Guardian Information
    father_name = forms.CharField(label="Father's Name", max_length=255, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    father_occupation = forms.CharField(label="Father's Occupation", max_length=255, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    father_phone = forms.CharField(label="Father's Phone", max_length=15, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    mother_name = forms.CharField(label="Mother's Name", max_length=255, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    mother_occupation = forms.CharField(label="Mother's Occupation", max_length=255, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    mother_phone = forms.CharField(label="Mother's Phone", max_length=15, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    guardian_name = forms.CharField(label="Guardian's Name", max_length=255, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    guardian_relationship = forms.CharField(label="Guardian's Relationship", max_length=100, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    guardian_phone = forms.CharField(label="Guardian's Phone", max_length=15, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))

    # Profile Picture
    profile_pic = forms.FileField(label="Profile Picture", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        
        # For Displaying Courses
        try:
            courses = Courses.objects.all()
            course_list = [(course.id, course.course_name) for course in courses]
        except:
            course_list = []
        
        # For Displaying Session Years
        try:
            session_years = SessionYearModel.objects.all()
            session_year_list = [(session_year.id, f"{session_year.session_start_year} to {session_year.session_end_year}") 
                               for session_year in session_years]
        except:
            session_year_list = []
        
        # Set the choices for the fields
        self.fields['course_id'].choices = course_list
        self.fields['session_year_id'].choices = session_year_list

class EditStudentForm(AddStudentForm):
    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        # Remove password field for editing
        del self.fields['password']