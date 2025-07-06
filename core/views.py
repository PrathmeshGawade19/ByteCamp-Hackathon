from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Prefetch
from .forms import ComplaintForm, ComplaintCommentForm
from .models import Category, Complaint, ComplaintUpvote, ComplaintComment
import json
import joblib
import os
from django.http import JsonResponse
from django.conf import settings

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'category_model.joblib')
category_model = joblib.load(MODEL_PATH)

MODEL_PATH = os.path.join(settings.BASE_DIR, 'category_model.pkl')
category_model = joblib.load(MODEL_PATH)

@login_required
def predict_category(request):
    desc = request.GET.get('desc', '')
    if desc:
        predicted = category_model.predict([desc])[0]
        return JsonResponse({'category': predicted})
    return JsonResponse({'category': None})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('dashboard')  
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('authority_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('login')

def public_home(request):
    trending_complaints = Complaint.objects.annotate(
        num_upvotes=Count('upvotes')
    ).order_by('-num_upvotes')[:5]  # top 5

    return render(request, 'core/public_home.html', {
        'trending_complaints': trending_complaints
    })

@login_required
def dashboard(request):
    latest_comments = Prefetch(
        'comments',
        queryset=ComplaintComment.objects.order_by('-created_at')[:2],
        to_attr='latest_comments'
    )

    trending_complaints = Complaint.objects.annotate(
        num_upvotes=Count('upvotes', distinct=True),
        num_comments=Count('comments', distinct=True)
    ).order_by('-num_upvotes')[:10].prefetch_related(latest_comments)

    my_complaints = Complaint.objects.filter(user=request.user).annotate(
        num_upvotes=Count('upvotes', distinct=True),
        num_comments=Count('comments', distinct=True)
    ).prefetch_related(latest_comments)

    map_complaints = Complaint.objects.exclude(status='Resolved')
    map_complaints_data = [
        {
            'category': c.category.name,
            'description': c.description,
            'location_name': c.location_name,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'image_url': c.image.url if c.image else '',
            'status': c.status
        }
        for c in map_complaints
    ]

    return render(request, 'core/dashboard.html', {
        'my_complaints': my_complaints,
        'trending_complaints': trending_complaints,
        'map_complaints_json': json.dumps(map_complaints_data, cls=DjangoJSONEncoder)
    })

@login_required
def file_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user

            # Predict category from description
            description = complaint.description
            predicted_category_name = category_model.predict([description])[0]

            # Look up category object
            category_obj = Category.objects.get(name=predicted_category_name)
            complaint.category = category_obj

            complaint.save()
            return redirect('dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'core/file_complaint.html', {'form': form})



def complaints_map(request):
    complaints = Complaint.objects.exclude(status='Resolved')
    complaints_data = [
        {
            'category': c.category.name,
            'description': c.description,
            'location_name': c.location_name,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'image_url': c.image.url if c.image else '',
            'status': c.status
        }
        for c in complaints
    ]
    return render(request, 'core/complaints_map.html', {'complaints': complaints_data})

@login_required
def upvote_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    upvote, created = ComplaintUpvote.objects.get_or_create(user=request.user, complaint=complaint)
    if not created:
        upvote.delete()  # toggle off
    return redirect('dashboard')

@login_required
def add_comment(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == "POST":
        form = ComplaintCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.complaint = complaint
            comment.save()
    return redirect('dashboard')

@staff_member_required
def authority_dashboard(request):
    
    complaints = Complaint.objects.all()
    # Get counts by status
    status_counts = {
        'Open': complaints.filter(status='Open').count(),
        'In_Progress': complaints.filter(status='In Progress').count(),
        'Resolved': complaints.filter(status='Resolved').count()
    }

    return render(request, 'core/authority_dashboard.html', {
        'complaints': complaints,
        'status_counts': status_counts
    })

@staff_member_required
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        complaint.status = new_status
        complaint.save()
    return redirect('authority_dashboard')

def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            ComplaintComment.objects.create(
                user=request.user,
                complaint=complaint,
                text=text
            )
            return redirect('complaint_detail', complaint_id=complaint.id)

    return render(request, 'core/complaint_detail.html', {
        'complaint': complaint
    })