from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from .forms import Image_form




# Create your views here.

def index(request):
    return render(request,'index.html')

# def login(request):
#     return render(request,'login.html')

def about_view(request):
    return render(request,'about.html')

def gallery_main_view(request):
    return render(request, 'gallery.html')

def contact_view(request):
    return render(request, 'contact.html')

def registration(request):
    rooms = RoomAvailability.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        roomtype = request.POST.get('roomtype')
        password = request.POST.get('password')

        # Check if room type is valid
        try:
            room_avail = RoomAvailability.objects.get(roomtype=roomtype)
        except RoomAvailability.DoesNotExist:
            messages.error(request, "Invalid room type selected.")
            return redirect('registration')

        # Check if any rooms of that type are available
        if room_avail.available_rooms <= 0:
            messages.error(request, f"No {roomtype} rooms available right now.")
            return redirect('registration')

        # Get capacity per room (1, 2, 3, 6)
        capacity = room_avail.capacity_per_room

        # Count students already in the current room
        current_students_in_room = Registration_table.objects.filter(
            roomtype=roomtype,
            roomnumber=room_avail.next_room_number
        ).count()

        # If the current room is full, move to the next room
        if current_students_in_room >= capacity:
            room_avail.next_room_number += 1
            room_avail.available_rooms -= 1
            room_avail.save()

        # Assign room number
        assigned_room_number = room_avail.next_room_number

        # Create student record
        Registration_table.objects.create(
            name=name,
            email=email,
            address=address,
            phone=phone,
            roomtype=roomtype,
            roomnumber=assigned_room_number,
            password=password
        )

        # Check again if the new room is full after adding
        total_students_now = Registration_table.objects.filter(
            roomtype=roomtype,
            roomnumber=assigned_room_number
        ).count()

        if total_students_now >= capacity:
            room_avail.next_room_number += 1
            room_avail.available_rooms -= 1
            room_avail.save()

        # Email message
        message=f'''
        Hi {name}, 
        Welcome to Hridayam Hostel.
        You have been successfully registered to HRIDHAYAM HOSTEL and your login credentials are 
        
        Username: {email}
        Password: {password}
        Roomtype: {roomtype}
        Room Number: {assigned_room_number}

        Regards,
        Hostel Admin
        '''

        send_mail(
            subject='Your Login Credentials - Hridhayam Hostel',
            message= message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list={email},
            fail_silently=False
        )

        # messages.success(request, f"{name} registered successfully and assigned Room No. {assigned_room_number}.")
        return redirect('hostel_admin_view')

    return render(request, 'registration.html', {'rooms': rooms})


ADMIN_EMAIL='hosteladmin@gmail.com'
ADMIN_PWD='hostel_admin'

def logout_view(request):
    request.session.flush()
    return redirect('login_view')

def hostel_admin_view(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    return render(request,'hostel_admin.html', {'announcements': announcements})

def hostel_student_view(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    return render(request,'hostel_student.html', {'announcements': announcements})


def login_view(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')

        # Admin login
        if email==ADMIN_EMAIL and password==ADMIN_PWD:
            request.session['role']='admin'
            request.session['email']=email
            return redirect('hostel_admin_view')
        
        # User login
        obj=Registration_table.objects.filter(email=email,password=password)
        # database table name= login page name 
        if obj.exists():
            user=obj.first()
            request.session['role']='user'
            request.session['mail']=user.email
            request.session['user_id']=user.id
            request.session['name']=user.name
            request.session['address']=user.address
            request.session['phone']=user.phone
            request.session['roomnumber']=user.roomnumber
            request.session['password']=user.password
            request.session['roomtype']=user.roomtype
            
            return redirect('hostel_student_view')
        else:
            msg='Invalid user email and password'
            return render(request,'login.html',{'msg':msg})
    return render(request,'login.html')

def student_list_view(request):
    students_list=Registration_table.objects.all()
    return render(request,'student_list.html',{'students_list':students_list})

def delete_student(request,student_id):
    std=Registration_table.objects.filter(id=student_id)
    if std.exists():
        std.delete()
    return redirect('student_list_view')

from django.contrib import messages
from .models import Registration_table, RoomAvailability

def edit_student(request, student_id):
    std = Registration_table.objects.get(id=student_id)
    rooms = RoomAvailability.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        roomtype = request.POST.get('roomtype')

        std.name = name
        std.email = email
        std.address = address
        std.phone = phone
        std.password = password

        # If room type has changed
        if roomtype != std.roomtype:
            try:
                new_room = RoomAvailability.objects.get(roomtype=roomtype)
            except RoomAvailability.DoesNotExist:
                messages.error(request, "Invalid room type selected.")
                return render(request, 'edit_student.html', {'std': std, 'rooms': rooms})

            # Capacity based on room type
            capacity = new_room.capacity_per_room

            # Check if any partially filled room exists
            existing_room = None
            for rn in range(1, new_room.next_room_number + 1):
                count_in_room = Registration_table.objects.filter(roomtype=roomtype, roomnumber=rn).count()
                if count_in_room < capacity:
                    existing_room = rn
                    break

            if not existing_room:
                if new_room.available_rooms <= 0:
                    messages.error(request, f"No {roomtype} rooms available.")
                    return render(request, 'edit_student.html', {'std': std, 'rooms': rooms})
                existing_room = new_room.next_room_number
                new_room.available_rooms -= 1
                new_room.next_room_number += 1

            # Free up the old room
            if std.roomtype:
                try:
                    old_room = RoomAvailability.objects.get(roomtype=std.roomtype)
                    old_room.available_rooms += 1
                    old_room.save()
                except RoomAvailability.DoesNotExist:
                    pass

            # Assign the new room
            std.roomnumber = existing_room
            std.roomtype = roomtype
            new_room.save()

        std.save()
        messages.success(request, f"Student updated successfully — Room No. {std.roomnumber}")
        return redirect('student_list_view')

    return render(request, 'edit_student.html', {'std': std, 'rooms': rooms})

# def warden_registration_view(request):
#     return render(request,'warden_registration.html')

# def warden_details_view(request):
#     if request.method=='POST':
#         name=request.POST.get('name')
#         # email=request.POST.get('email')
#         age=request.POST.get('age')
#         address=request.POST.get('address')
#         gender=request.POST.get('gender')
#         phone=request.POST.get('phone')

#         obj=Warden.objects.create(
#             name=name,
#             age=age,
#             address=address,
#             gender=gender,
#             phone=phone,
#             # roomtype=roomtype,
#             # roomnumber=roomnumber,
#             # password=password
#         )
#         obj.save()
#         return redirect('warden_list_view')  # redirect after save
#     return redirect('warden_registration_view')

# def warden_list_view(request):
#     wardens=Warden.objects.all()
#     return render(request,'warden_details.html',{'wardens':wardens})

def upload_images(request):
    if request.method=='POST':
        form=Image_form(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_list_admin')
    else:
        forms=Image_form()
    return render(request,'upload_images.html',{'forms':forms})

def image_list_admin(request):
    images=Image_table.objects.all()
    return render(request,'image_list_admin.html',{'images':images})

def delete_images(request,i_id):
    image=Image_table.objects.filter(id=i_id)
    if image.exists():
        image.delete()
    return redirect('image_list_admin')

def update_images(request,i_id):
    image=Image_table.objects.filter(id=i_id).first()
    if not image:
        return redirect('image_list_admin')
    if request.method=='POST':
        form=Image_form(request.POST,request.FILES,instance=image)
        if form.is_valid():
            form.save()
            return redirect('image_list_admin')
    else:
        form=Image_form(instance=image)
    return render(request,'update_images.html',{'form':form})


def announcement_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        Announcement.objects.create(
            title=title, 
            message=message
        )
        return redirect('announcement_list_view')
    return render(request, 'announcement_create.html')

def announcement_list_view(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    return render(request, 'announcement_list.html', {'announcements': announcements})

def delete_announcements(request,i_id):
    ann=Announcement.objects.filter(id=i_id)
    if ann.exists():
        ann.delete()
    return redirect('announcement_list_view')

def update_announcements(request, i_id):
    ann = get_object_or_404(Announcement, id=i_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        # date_posted = request.POST.get('date')  

        ann.title = title
        ann.message = message
        # if date_posted:
        #     ann.date_posted = date_posted  
        ann.save()

        return redirect('announcement_list_view')
    return render(request, 'update_announcements.html', {'ann': ann})

def gallery_view(request):
    images=Image_table.objects.all()
    return render(request,'gallery_admin.html',{'images':images})

# from django.shortcuts import render
# from .models import RoomAvailability, Registration_table

def room_status_view(request):
    room_data = []

    # Loop through each room type
    for room in RoomAvailability.objects.all():
        # Count how many students are currently in that type
        occupied_count = Registration_table.objects.filter(roomtype=room.roomtype).count()

        # Rooms that are completely filled
        fully_occupied = occupied_count // room.capacity_per_room

        # Rooms that are partially filled
        partial = 1 if (occupied_count % room.capacity_per_room != 0 and occupied_count < room.total_rooms * room.capacity_per_room) else 0

        # Available rooms = total - fully occupied - partially filled (if any)
        available = room.total_rooms - fully_occupied - partial

        room_data.append({
            'roomtype': room.roomtype,
            'total_rooms': room.total_rooms,
            'fully_occupied': fully_occupied,
            'partially_filled': partial,
            'available_rooms': available,
        })

    return render(request, 'room_status.html', {'room_data': room_data})

def student_profile(request):
    return render(request,'student_my_profile.html')


def student_complaints(request):
    email = request.session.get('mail')
    if not email:
        return redirect('login_view')

    student = Registration_table.objects.get(email=email)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        if title and description:
            Complaint_tab.objects.create(
                student=student,
                title=title,
                description=description
            )
        return redirect("student_complaints")

    complaints = Complaint_tab.objects.filter(student=student).order_by('-date_created')
    return render(request, 'student_complaints.html', {'complaints': complaints, 'student': student})


def admin_complaints(request):
    complaints = Complaint_tab.objects.all().order_by('-date_created')
    return render(request, "admin_complaints.html", {'complaints': complaints})


def reply_complaint(request, id):
    complaint = get_object_or_404(Complaint_tab, id=id)

    if request.method == "POST":
        reply_text = request.POST.get("reply")
        status = request.POST.get("status")
        complaint.reply = reply_text
        complaint.status = status
        complaint.save()
        return redirect("admin_complaints")

    return render(request, "reply_complaint.html", {'complaint': complaint})

def request_cleaning(request):
    if request.method == "POST":
        email = request.session.get('mail')
        student = Registration_table.objects.get(email=email)

        Complaint_tab.objects.create(
            student=student,
            title="Room Cleaning Request",
            description=f"Room cleaning requested by {student.name} for room {student.roomnumber}.",
            status="Pending"
        )
        messages.success(request, "Cleaning request sent successfully!")
        return redirect('student_complaints') 

    return redirect('hostel_student_view')

def request_maintenance(request):
    if request.method == "POST":
        email = request.session.get('mail')
        student = Registration_table.objects.get(email=email)

        Complaint_tab.objects.create(
            student=student,
            title="Room Maintenance Request",
            description=f"Room maintenance requested by {student.name} for room {student.roomnumber}.",
            status="Pending"
        )

        messages.success(request, " Maintenance request sent successfully!")
        return redirect('student_complaints')

    return redirect('hostel_student_view')

def mess_menu(request):
    return render(request, "mess_menu.html")

def student_announcement_list_view(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    return render(request,'student_announcements.html',{'announcements':announcements})

