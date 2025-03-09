from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError



class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField(null=True, blank=True)
    session_end_year = models.DateField(null=True, blank=True)
    objects = models.Manager()



# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    email = models.EmailField(unique=True)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    # Personal Information
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,null=True, blank=True)   
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # Professional Information
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    qualifications = models.TextField(null=True, blank=True)
    specialization = models.CharField(max_length=200, null=True, blank=True)
    
    # Documents
   
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name} - {self.designation}"

    def calculate_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'



class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    # def __str__(self):
	#     return self.course_name



class Subjects(models.Model):
    id =models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255, null=True, blank=True)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True) #need to give defauult course
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()



class Students(models.Model):
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
        ('HI', 'Hindi'),
        ('ML', 'Malayalam'),
    )

    # Basic Information
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Personal Information
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='student_profile_pics/', null=True, blank=True)  # Add this line
    
    # Academic Information
    course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING, null=True, blank=True)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, null=True, blank=True)
    second_language = models.CharField(
        max_length=2,
        choices=SECOND_LANGUAGE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Second Language"
    )
    
    # Parent/Guardian Information
    father_name = models.CharField(max_length=255, null=True, blank=True)
    father_occupation = models.CharField(max_length=255, null=True, blank=True)
    father_phone = models.CharField(max_length=15, null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    mother_occupation = models.CharField(max_length=255, null=True, blank=True)
    mother_phone = models.CharField(max_length=15, null=True, blank=True)
    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_relationship = models.CharField(max_length=100, null=True, blank=True)
    guardian_phone = models.CharField(max_length=15, null=True, blank=True)


    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name} ({self.admission_number})"

    def calculate_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def get_current_semester(self):
        # Logic to calculate current semester based on admission date
        from datetime import date
        if self.created_at:
            months_enrolled = (date.today().year - self.created_at.year) * 12 + \
                            (date.today().month - self.created_at.month)
            return (months_enrolled // 6) + 1
        return 1

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['-created_at']


class Attendance(models.Model):
    # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING, null=True, blank=True)
    attendance_date = models.DateField(null=True, blank=True)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING, null=True, blank=True)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE, null=True, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, null=True, blank=True)
    leave_date = models.CharField(max_length=255, null=True, blank=True)
    leave_message = models.TextField(null=True, blank=True)
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()



class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


#Creating Django Signals

# It's like trigger in database. It will run only when Data is Added in CustomUser model

@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(
                admin=instance,
                course_id=Courses.objects.get(id=1),
                session_year_id=SessionYearModel.objects.get(id=1)
            )
    

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):  # pylint: disable=unused-argument
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()



# Add these models to your student_management_app/models.py file

class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    staff_in_charge = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    id = models.AutoField(primary_key=True)
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    status_choices = ((0, "Pending"), (1, "Approved"), (2, "Rejected"))
    status = models.IntegerField(default=0, choices=status_choices)
    application_date = models.DateTimeField(auto_now_add=True)
    application_message = models.TextField()
    feedback = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        # Ensure a student can only apply once to a specific club
        unique_together = ('club_id', 'student_id')


class ScholarshipType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.name


class ScholarshipApplication(models.Model):
    id = models.AutoField(primary_key=True)
    scholarship_type = models.ForeignKey(ScholarshipType, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    status_choices = ((0, "Pending"), (1, "Approved"), (2, "Rejected"))
    status = models.IntegerField(default=0, choices=status_choices)
    application_date = models.DateTimeField(auto_now_add=True)
    family_income = models.DecimalField(max_digits=12, decimal_places=2)
    academic_achievements = models.TextField()
    extra_curricular_achievements = models.TextField(blank=True, null=True)
    purpose_statement = models.TextField()
    supporting_documents = models.FileField(upload_to='scholarship_docs/')
    hod_feedback = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        # Ensure a student can only apply once to a specific scholarship type per academic year
        unique_together = ('scholarship_type', 'student_id', 'application_date')




# Add after your existing models

class TimeSlot(models.Model):
    id = models.AutoField(primary_key=True)
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def __str__(self):
        return f"Period {self.period_number} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    class Meta:
        ordering = ['period_number']

class Timetable(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True)
    day_choices = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')
    )
    day = models.CharField(choices=day_choices, null=True, blank=True,max_length=100)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey(Staffs, on_delete=models.CASCADE, null=True, blank=True)
    room_number = models.CharField(max_length=50, null=True, blank=True)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        unique_together = [
            ('course', 'day', 'time_slot', 'session_year'),  # No two classes at same time for a course
            ('staff', 'day', 'time_slot', 'session_year'),   # No teacher can teach two classes at same time
            ('room_number', 'day', 'time_slot', 'session_year')  # No two classes in same room at same time
        ]

    def clean(self):
        # Validate if the staff teaches this subject
        if not Subjects.objects.filter(
            staff_id=self.staff.admin,
            id=self.subject.id
        ).exists():
            raise ValidationError(
                f"Staff member {self.staff.admin.first_name} is not assigned to teach {self.subject.subject_name}"
            )

        # Validate if subject belongs to the course
        if self.subject.course_id != self.course:
            raise ValidationError(
                f"Subject {self.subject.subject_name} is not part of course {self.course.course_name}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.course_name} - {self.get_day_display()} - Period {self.time_slot.period_number}"



