from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('file-complaint/', views.file_complaint, name='file_complaint'),
    path('complaints-map/', views.complaints_map, name='complaints_map'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upvote/<int:complaint_id>/', views.upvote_complaint, name='upvote_complaint'),
    path('comment/<int:complaint_id>/', views.add_comment, name='add_comment'),
    path('authority/', views.authority_dashboard, name='authority_dashboard'),
    path('authority/update-status/<int:complaint_id>/', views.update_complaint_status, name='update_complaint_status'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('predict_category/', views.predict_category, name='predict_category'),

]
