from django import forms 
from django.forms import Form
from student_management_app.models import Courses, SessionYearModel


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    # These fields will be populated in __init__
    course_id = forms.ChoiceField(label="Course", widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        
        # For Displaying Courses - Move this here from class level
        try:
            courses = Courses.objects.all()
            course_list = []
            for course in courses:
                single_course = (course.id, course.course_name)
                course_list.append(single_course)
        except:
            course_list = []
        
        # For Displaying Session Years - Move this here from class level
        try:
            session_years = SessionYearModel.objects.all()
            session_year_list = []
            for session_year in session_years:
                single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
                session_year_list.append(single_session_year)
                
        except:
            session_year_list = []
        
        # Set the choices for the fields
        self.fields['course_id'].choices = course_list
        self.fields['session_year_id'].choices = session_year_list


class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    # These fields will be populated in __init__
    course_id = forms.ChoiceField(label="Course", widget=forms.Select(attrs={"class":"form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        
        # For Displaying Courses - Move this here from class level
        try:
            courses = Courses.objects.all()
            course_list = []
            for course in courses:
                single_course = (course.id, course.course_name)
                course_list.append(single_course)
        except:
            course_list = []
        
        # For Displaying Session Years - Move this here from class level
        try:
            session_years = SessionYearModel.objects.all()
            session_year_list = []
            for session_year in session_years:
                single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
                session_year_list.append(single_session_year)
                
        except:
            session_year_list = []
        
        # Set the choices for the fields
        self.fields['course_id'].choices = course_list
        self.fields['session_year_id'].choices = session_year_list