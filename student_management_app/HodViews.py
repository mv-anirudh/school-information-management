from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from student_management_app.models import CustomUser, ScholarshipApplication, ScholarshipType, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm
from .models import TimeSlot, Timetable
from django.db.models import Q


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        try:
            form = AddStudentForm(request.POST, request.FILES)
            
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                gender = form.cleaned_data['gender']
                session_year_id = form.cleaned_data['session_year_id']
                course_id = form.cleaned_data['course_id']
                
                # Get additional fields
                religion = form.cleaned_data.get('religion')
                caste = form.cleaned_data.get('caste')
                
                # Create CustomUser
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=3  # Student user type
                )
                
                # Get Course and Session Year instances
                course = Courses.objects.get(id=course_id)
                session_year = SessionYearModel.objects.get(id=session_year_id)
                
                # Update Student profile
                student = Students.objects.get(admin=user)
                student.gender = gender
                student.session_year_id = session_year
                student.course_id = course
                
                # Handle profile picture upload
                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage()
                    filename = fs.save(profile_pic.name, profile_pic)
                    profile_pic_url = fs.url(filename)
                    student.profile_pic = profile_pic_url
                
                # Update optional fields if provided
                if form.cleaned_data.get('date_of_birth'):
                    student.date_of_birth = form.cleaned_data['date_of_birth']
                if form.cleaned_data.get('blood_group'):
                    student.blood_group = form.cleaned_data['blood_group']
                if form.cleaned_data.get('phone_number'):
                    student.phone_number = form.cleaned_data['phone_number']
                if form.cleaned_data.get('address'):
                    student.address = form.cleaned_data['address']
                if form.cleaned_data.get('second_language'):
                    student.second_language = form.cleaned_data['second_language']
                
                # Save parent/guardian information
                student.father_name = form.cleaned_data.get('father_name', '')
                student.father_occupation = form.cleaned_data.get('father_occupation', '')
                student.father_phone = form.cleaned_data.get('father_phone', '')
                student.mother_name = form.cleaned_data.get('mother_name', '')
                student.mother_occupation = form.cleaned_data.get('mother_occupation', '')
                student.mother_phone = form.cleaned_data.get('mother_phone', '')
                
                # Update Student profile with new fields
                student.religion = religion
                student.caste = caste
                
                student.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            else:
                messages.error(request, f"Failed to Add Student! Form Errors: {form.errors}")
                return redirect('add_student')
                
        except Exception as e:
            messages.error(request, f"Failed to Add Student! Error: {str(e)}")
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    course_filter = request.GET.get('course')
    language_filter = request.GET.get('language')
    
    if course_filter:
        students = students.filter(course_id=course_filter)
    if language_filter:
        students = students.filter(second_language=language_filter)
    
    context = {
        "students": students,
        'courses': Courses.objects.all(),
        'second_languages': Students.SECOND_LANGUAGE_CHOICES,
    }
    return render(request, "hod_template/manage_student_template.html", context)


def edit_student(request, student_id):
    """Edit student information"""
    try:
        # Get student instance
        student = Students.objects.get(admin=student_id)
        form = EditStudentForm(initial={
            'email': student.admin.email,
            'username': student.admin.username,
            'first_name': student.admin.first_name,
            'last_name': student.admin.last_name,
            'address': student.address,
            'course_id': student.course_id.id if student.course_id else None,
            'gender': student.gender,
            'session_year_id': student.session_year_id.id if student.session_year_id else None,
            'blood_group': student.blood_group,
            'date_of_birth': student.date_of_birth,
            'phone_number': student.phone_number,
            'second_language': student.second_language,
            'father_name': student.father_name,
            'father_occupation': student.father_occupation,
            'father_phone': student.father_phone,
            'mother_name': student.mother_name,
            'mother_occupation': student.mother_occupation,
            'mother_phone': student.mother_phone,
        })
        
        # Store student_id in session
        request.session['student_id'] = student_id

        context = {
            "form": form,
            "id": student_id,
            "username": student.admin.username,
            "profile_pic": student.profile_pic
        }
        return render(request, "hod_template/edit_student_template.html", context)

    except Students.DoesNotExist:
        messages.error(request, "Student Not Found!")
        return redirect('manage_student')
    except Exception as e:
        messages.error(request, f"Failed to Edit Student: {str(e)}")
        return redirect('manage_student')


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Courses.objects.get(id=course_id)
                student_model.course_id = course

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Failed to Uupdate Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass



# Add these views to hod_views.py or create a new file if needed

def admin_manage_scholarships(request):
    scholarships = ScholarshipType.objects.all()
    
    context = {
        "scholarships": scholarships
    }
    return render(request, 'hod_template/admin_manage_scholarships.html', context)


def admin_add_scholarship(request):
    if request.method != "POST":
        return render(request, 'hod_template/admin_add_scholarship.html')
    else:
        name = request.POST.get('name')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        
        try:
            scholarship = ScholarshipType(
                name=name,
                description=description,
                amount=amount
            )
            scholarship.save()
            messages.success(request, "Scholarship added successfully!")
            return redirect('admin_manage_scholarships')
        except Exception as e:
            messages.error(request, f"Failed to add scholarship: {str(e)}")
            return redirect('admin_add_scholarship')


def admin_view_scholarship_applications(request):
    applications = ScholarshipApplication.objects.all()
    
    context = {
        "applications": applications
    }
    return render(request, 'hod_template/admin_view_scholarship_applications.html', context)


def admin_view_scholarship_application_detail(request, application_id):
    application = ScholarshipApplication.objects.get(id=application_id)
    
    context = {
        "application": application
    }
    return render(request, 'hod_template/admin_view_scholarship_application_detail.html', context)


def approve_scholarship_application(request, application_id):
    """
    Approve a scholarship application with feedback
    """
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    try:
        application = ScholarshipApplication.objects.get(id=application_id)
        feedback = request.POST.get('feedback')
        
        # Update application status
        application.status = 1  # Approved
        application.admin_feedback = feedback
        application.save()
        
        # Send notification to student (you might want to implement this)
        # notify_student(application.student_id, "Your scholarship application has been approved!")
        
        messages.success(request, "Scholarship application approved successfully!")
        return redirect('admin_view_scholarship_applications')
    
    except ScholarshipApplication.DoesNotExist:
        messages.error(request, "Application not found!")
        return redirect('admin_view_scholarship_applications')

def reject_scholarship_application(request, application_id):
    """
    Reject a scholarship application with feedback
    """
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    try:
        application = ScholarshipApplication.objects.get(id=application_id)
        feedback = request.POST.get('feedback')
        
        # Update application status
        application.status = 2  # Rejected
        application.admin_feedback = feedback
        application.save()
        
        # Send notification to student (you might want to implement this)
        # notify_student(application.student_id, "Your scholarship application has been rejected.")
        
        messages.success(request, "Scholarship application rejected with feedback.")
        return redirect('admin_view_scholarship_applications')
    
    except ScholarshipApplication.DoesNotExist:
        messages.error(request, "Application not found!")
        return redirect('admin_view_scholarship_applications')
    
def admin_view_scholarship_application_detail(request, application_id):
    """
    View detailed information about a specific scholarship application
    """
    try:
        application = ScholarshipApplication.objects.get(id=application_id)
        context = {
            "application": application
        }
        return render(request, 'hod_template/admin_view_scholarship_application_detail.html', context)
    except ScholarshipApplication.DoesNotExist:
        messages.error(request, "Application not found!")
        return redirect('admin_view_scholarship_applications')


def manage_timetable(request):
    """View all timetables"""
    timetables = Timetable.objects.all()
    courses = Courses.objects.all()
    time_slots = TimeSlot.objects.all()
    subjects = Subjects.objects.all()
    staffs = Staffs.objects.all()
    day_filter = request.GET.get('day')
    timetables = Timetable.objects.all().order_by('day', 'time_slot__start_time')
    course_filter = request.GET.get('course')
    
    
    if day_filter:
        timetables = timetables.filter(day=day_filter)
    if course_filter:
        timetables = timetables.filter(course_id=course_filter)
    
    
    context = {
        "timetables": timetables,
        "courses": courses,
        "time_slots": time_slots,
        "subjects": subjects,
        "staffs": staffs,
        "days": Timetable.day_choices,
        'selected_day': day_filter,
        'selected_course': course_filter
    }
    return render(request, 'hod_template/manage_timetable.html', context)

def add_timetable(request):
    """Add new timetable entry"""
    if request.method != "POST":
        courses = Courses.objects.all()
        time_slots = TimeSlot.objects.all()
        subjects = Subjects.objects.all()
        staffs = Staffs.objects.all()
        session_years = SessionYearModel.objects.all()  # Add this line
        
        context = {
            "courses": courses,
            "time_slots": time_slots,
            "subjects": subjects,
            "staffs": staffs,
            "days": Timetable.day_choices,
            "session_years": session_years  # Add this line
        }
        return render(request, 'hod_template/add_timetable.html', context)
    else:
        try:
            course_id = request.POST.get('course')
            day = request.POST.get('day')
            time_slot_id = request.POST.get('time_slot')
            subject_id = request.POST.get('subject')
            staff_id = request.POST.get('staff')
            room_number = request.POST.get('room_number')
            session_year_id = request.POST.get('session_year')

            # Get model instances
            course = Courses.objects.get(id=course_id)
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            subject = Subjects.objects.get(id=subject_id)
            staff = Staffs.objects.get(id=staff_id)
            session_year = SessionYearModel.objects.get(id=session_year_id)

            # Check for conflicts
            conflicts = Timetable.objects.filter(
                Q(course=course, day=day, time_slot=time_slot, session_year=session_year) |
                Q(staff=staff, day=day, time_slot=time_slot, session_year=session_year) |
                Q(room_number=room_number, day=day, time_slot=time_slot, session_year=session_year)
            )

            if conflicts.exists():
                messages.error(request, "Time slot conflict detected! Please choose another slot.")
                return redirect('add_timetable')

            # Create timetable entry
            timetable = Timetable(
                course=course,
                day=day,
                time_slot=time_slot,
                subject=subject,
                staff=staff,
                room_number=room_number,
                session_year=session_year
            )
            timetable.save()
            
            messages.success(request, "Timetable entry added successfully!")
            return redirect('manage_timetable')
            
        except Exception as e:
            messages.error(request, f"Failed to add timetable entry: {str(e)}")
            return redirect('add_timetable')

def edit_timetable(request, timetable_id):
    """Edit existing timetable entry"""
    if request.method != "POST":
        try:
            timetable = Timetable.objects.get(id=timetable_id)
            courses = Courses.objects.all()
            time_slots = TimeSlot.objects.all()
            subjects = Subjects.objects.all()
            staffs = Staffs.objects.all()
            
            context = {
                "timetable": timetable,
                "courses": courses,
                "time_slots": time_slots,
                "subjects": subjects,
                "staffs": staffs,
                "days": Timetable.day_choices
            }
            return render(request, 'hod_template/edit_timetable.html', context)
        
        except Timetable.DoesNotExist:
            messages.error(request, "Timetable entry not found!")
            return redirect('manage_timetable')
    else:
        try:
            timetable_id = request.POST.get('timetable_id')
            course_id = request.POST.get('course')
            day = request.POST.get('day')
            time_slot_id = request.POST.get('time_slot')
            subject_id = request.POST.get('subject')
            staff_id = request.POST.get('staff')
            room_number = request.POST.get('room_number')
            session_year_id = request.POST.get('session_year')

            # Get model instances
            timetable = Timetable.objects.get(id=timetable_id)
            course = Courses.objects.get(id=course_id)
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            subject = Subjects.objects.get(id=subject_id)
            staff = Staffs.objects.get(id=staff_id)
            session_year = SessionYearModel.objects.get(id=session_year_id)

            # Check for conflicts excluding current entry
            conflicts = Timetable.objects.filter(
                Q(course=course, day=day, time_slot=time_slot, session_year=session_year) |
                Q(staff=staff, day=day, time_slot=time_slot, session_year=session_year) |
                Q(room_number=room_number, day=day, time_slot=time_slot, session_year=session_year)
            ).exclude(id=timetable_id)

            if conflicts.exists():
                messages.error(request, "Time slot conflict detected! Please choose another slot.")
                return redirect('edit_timetable', timetable_id=timetable_id)

            # Update timetable entry
            timetable.course = course
            timetable.day = day
            timetable.time_slot = time_slot
            timetable.subject = subject
            timetable.staff = staff
            timetable.room_number = room_number
            timetable.session_year = session_year
            timetable.save()
            
            messages.success(request, "Timetable entry updated successfully!")
            return redirect('manage_timetable')
            
        except Exception as e:
            messages.error(request, f"Failed to update timetable entry: {str(e)}")
            return redirect('edit_timetable', timetable_id=timetable_id)

def delete_timetable(request, timetable_id):
    """Delete timetable entry"""
    try:
        timetable = Timetable.objects.get(id=timetable_id)
        timetable.delete()
        messages.success(request, "Timetable entry deleted successfully!")
    except Timetable.DoesNotExist:
        messages.error(request, "Timetable entry not found!")
    except Exception as e:
        messages.error(request, f"Failed to delete timetable entry: {str(e)}")
    
    return redirect('manage_timetable')

def manage_time_slots(request):
    """View all time slots"""
    time_slots = TimeSlot.objects.all().order_by('period_number')
    context = {
        "time_slots": time_slots
    }
    return render(request, 'hod_template/manage_time_slots.html', context)

def add_time_slot(request):
    """Add new time slot"""
    if request.method != "POST":
        return render(request, 'hod_template/add_time_slot.html')
    else:
        try:
            period_number = request.POST.get('period_number')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            # Create time slot
            time_slot = TimeSlot(
                period_number=period_number,
                start_time=start_time,
                end_time=end_time
            )
            time_slot.full_clean()  # This will run model validation
            time_slot.save()
            
            messages.success(request, "Time slot added successfully!")
            return redirect('manage_time_slots')
            
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e.messages[0]}")
            return redirect('add_time_slot')
        except Exception as e:
            messages.error(request, f"Failed to add time slot: {str(e)}")
            return redirect('add_time_slot')

def edit_time_slot(request, time_slot_id):
    """Edit existing time slot"""
    if request.method != "POST":
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            context = {
                "time_slot": time_slot
            }
            return render(request, 'hod_template/edit_time_slot.html', context)
        
        except TimeSlot.DoesNotExist:
            messages.error(request, "Time slot not found!")
            return redirect('manage_time_slots')
    else:
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            time_slot.period_number = request.POST.get('period_number')
            time_slot.start_time = request.POST.get('start_time')
            time_slot.end_time = request.POST.get('end_time')

            time_slot.full_clean()  # Run validation
            time_slot.save()
            
            messages.success(request, "Time slot updated successfully!")
            return redirect('manage_time_slots')
            
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e.messages[0]}")
            return redirect('edit_time_slot', time_slot_id=time_slot_id)
        except Exception as e:
            messages.error(request, f"Failed to update time slot: {str(e)}")
            return redirect('edit_time_slot', time_slot_id=time_slot_id)

def delete_time_slot(request, time_slot_id):
    """Delete time slot"""
    try:
        time_slot = TimeSlot.objects.get(id=time_slot_id)
        # Check if time slot is being used in any timetable
        if Timetable.objects.filter(time_slot=time_slot).exists():
            messages.error(request, "Cannot delete time slot as it is being used in timetable!")
            return redirect('manage_time_slots')
            
        time_slot.delete()
        messages.success(request, "Time slot deleted successfully!")
    except TimeSlot.DoesNotExist:
        messages.error(request, "Time slot not found!")
    except Exception as e:
        messages.error(request, f"Failed to delete time slot: {str(e)}")
    
    return redirect('manage_time_slots')

