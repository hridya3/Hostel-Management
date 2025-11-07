from django.db import models
from django.utils import timezone

# Create your models here.

class Registration_table(models.Model):
    ROOM_TYPES = [
        ('Single', 'Single Room'),
        ('Double', 'Double Room'),
        ('Triple', 'Triple Room'),
        ('Six', 'Six Share'),
    ]
    name=models.CharField(max_length=50,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    address=models.CharField(max_length=50,null=True,blank=True)
    phone=models.CharField(max_length=13,null=True,blank=True)
    password=models.CharField(max_length=20,null=True,blank=True)
    roomnumber=models.IntegerField(null=True,blank=True)
    roomtype = models.CharField(max_length=20, choices=ROOM_TYPES, null=True, blank=True)    

class RoomAvailability(models.Model):
    ROOM_TYPES = [
        ('Single', 'Single Room'),
        ('Double', 'Double Room'),
        ('Triple', 'Triple Room'),
        ('Six', 'Six Share'),
    ]

    roomtype = models.CharField(max_length=20, choices=ROOM_TYPES, unique=True)
    total_rooms = models.PositiveIntegerField(default=0)
    available_rooms = models.PositiveIntegerField(default=0)
    next_room_number = models.PositiveIntegerField(default=1)
    capacity_per_room = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        capacity_map = {
            'Single': 1,
            'Double': 2,
            'Triple': 3,
            'Six': 6
        }
        # automatically set based on type
        self.capacity_per_room = capacity_map.get(self.roomtype, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.roomtype} - {self.available_rooms}/{self.total_rooms} available"
    
class Warden(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Image_table(models.Model):
    name=models.CharField(max_length=50)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to='products/')
    # added_on=models.DateTimeField(auto_now_add=True)

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
class StudentProfile(models.Model):
    student = models.OneToOneField(Registration_table, on_delete=models.CASCADE)
    gender = models.CharField(max_length=15, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.student.name}'s Profile"

class Complaint_tab(models.Model):
    student = models.ForeignKey(Registration_table, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=20, default='Pending')
    reply = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.student.name}"

