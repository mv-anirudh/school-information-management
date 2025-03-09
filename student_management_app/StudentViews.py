from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.db.models import Avg
import datetime # To Parse input DateTime into Python Date Time Object

from student_management_app.forms import EditStudentForm
from student_management_app.models import Club, ClubMembership, CustomUser, ScholarshipApplication, ScholarshipType, Staffs, Courses, Subjects, Students, Attendance, AttendanceReport, LeaveReportStudent, FeedBackStudent, StudentResult, Timetable


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()

    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "student_template/student_home_template.html", context)


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id) # Getting Logged in Student Data
    course = student.course_id # Getting Course Enrolled of LoggedIn Student
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    subjects = Subjects.objects.filter(course_id=course) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the Input Data
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
        subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        stud_obj = Students.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse), subject_id=subject_obj)
        # Getting Attendance Report based on the attendance details obtained above
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        }

        return render(request, 'student_template/student_attendance_data.html', context)
       

def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'student_template/student_apply_leave.html', context)


def student_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = Students.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('student_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('student_apply_leave')


def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'student_template/student_feedback.html', context)


def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('student_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = Students.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('student_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('student_feedback')


def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def student_view_result(request):
    student = Students.objects.get(admin=request.user.id)
    student_result = StudentResult.objects.filter(student_id=student.id)
    
    # Calculate statistics
    passed_count = student_result.filter(subject_exam_marks__gte=40).count()
    total_count = student_result.count()
    failed_count = total_count - passed_count
    average_score = student_result.aggregate(Avg('subject_exam_marks'))['subject_exam_marks__avg']

    context = {
        "student_result": student_result,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "average_score": round(average_score) if average_score else 0,
        "current_user": request.user.username,
      
    }
    return render(request, "student_template/student_view_result.html", context)



# Add these views to student_views.py or create a new file if needed

def student_view_clubs(request):
    student = Students.objects.get(admin=request.user.id)
    clubs = Club.objects.all()
    
    # Get clubs the student has already applied to
    applied_clubs = ClubMembership.objects.filter(student_id=student)
    applied_club_ids = [membership.club_id.id for membership in applied_clubs]
    
    context = {
        "clubs": clubs,
        "applied_club_ids": applied_club_ids,
        "applied_clubs": applied_clubs
    }
    return render(request, 'student_template/student_view_clubs.html', context)


def student_apply_club(request):
    if request.method == "GET":
        club_id = request.GET.get('club_id')
        try:
            club = Club.objects.get(id=club_id)
            context = {
                "club": club
            }
            return render(request, 'student_template/student_apply_club.html', context)
        except Club.DoesNotExist:
            messages.error(request, "Club not found!")
            return redirect('student_view_clubs')
            
    elif request.method == "POST":
        club_id = request.POST.get('club_id')
        message = request.POST.get('message')
        
        student = Students.objects.get(admin=request.user.id)
        club = Club.objects.get(id=club_id)
        
        try:
            existing_application = ClubMembership.objects.get(club_id=club, student_id=student)
            messages.error(request, "You have already applied to this club!")
            return redirect('student_view_clubs')
        except ClubMembership.DoesNotExist:
            club_membership = ClubMembership(
                club_id=club,
                student_id=student,
                application_message=message
            )
            club_membership.save()
            messages.success(request, "Successfully applied for club membership!")
            return redirect('student_view_clubs')
    
    return HttpResponse("<h2>Method Not Allowed</h2>")


def student_view_scholarships(request):
    student = Students.objects.get(admin=request.user.id)
    scholarships = ScholarshipType.objects.all()
    
    # Get scholarships the student has already applied for
    applications = ScholarshipApplication.objects.filter(student_id=student)
    applied_scholarship_ids = [app.scholarship_type.id for app in applications]
    
    context = {
        "scholarships": scholarships,
        "applied_scholarship_ids": applied_scholarship_ids,
        "applications": applications
    }
    return render(request, 'student_template/student_view_scholarships.html', context)


def student_apply_scholarship(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        scholarship_id = request.POST.get('scholarship_id')
        family_income = request.POST.get('family_income')
        academic_achievements = request.POST.get('academic_achievements')
        extra_curricular = request.POST.get('extra_curricular')
        purpose = request.POST.get('purpose')
        
        if request.FILES.get('documents'):
            documents = request.FILES['documents']
        else:
            messages.error(request, "Supporting documents are required!")
            return redirect('student_view_scholarships')
        
        student = Students.objects.get(admin=request.user.id)
        scholarship = ScholarshipType.objects.get(id=scholarship_id)
        
        # Check if already applied to this scholarship
        try:
            existing_application = ScholarshipApplication.objects.get(
                scholarship_type=scholarship,
                student_id=student,
                application_date__year=datetime.datetime.now().year
            )
            messages.error(request, "You have already applied for this scholarship this year!")
            return redirect('student_view_scholarships')
        except ScholarshipApplication.DoesNotExist:
            # Create new application
            application = ScholarshipApplication(
                scholarship_type=scholarship,
                student_id=student,
                family_income=family_income,
                academic_achievements=academic_achievements,
                extra_curricular_achievements=extra_curricular,
                purpose_statement=purpose,
                supporting_documents=documents
            )
            application.save()
            messages.success(request, "Scholarship application submitted successfully!")
            return redirect('student_view_scholarships')


def edit_student(request, student_id):
    try:
        student = Students.objects.get(admin=student_id)
        form = EditStudentForm(initial={
            # ...existing fields...
            'religion': student.religion,
            'caste': student.caste,
        })
        return render(request, 'edit_student.html', {'form': form, 'student': student})
    except Students.DoesNotExist:
        messages.error(request, "Student not found!")
        return redirect('manage_student')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('manage_student')


def student_view_timetable(request):
    try:
        student = Students.objects.get(admin=request.user)
        day_filter = request.GET.get('day')
        
        # Base queryset
        timetable = Timetable.objects.filter(course=student.course_id)
        
        # Apply day filter if selected
        if day_filter:
            timetable = timetable.filter(day=day_filter)
        
        # Group timetable by day
        timetable_by_day = {}
        for entry in timetable.order_by('day', 'time_slot__start_time'):
            if entry.day not in timetable_by_day:
                timetable_by_day[entry.day] = []
            timetable_by_day[entry.day].append(entry)
        
        context = {
            'student': student,
            'timetable_by_day': timetable_by_day,
            'days': Timetable.day_choices,
        }
        return render(request, 'student_template/student_view_timetable.html', context)
        
    except Exception as e:
        messages.error(request, f"Error fetching timetable: {str(e)}")
        return redirect('student_home')