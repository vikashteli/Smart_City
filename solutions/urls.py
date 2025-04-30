from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('', views.home, name='home'),
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('ideas/<int:pk>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:pk>/edit/', views.idea_edit, name='idea_edit'),
    path('ideas/<int:pk>/vote/', views.idea_vote, name='idea_vote'),
    path('ideas/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('ideas/<int:pk>/update-status/', views.update_idea_status, name='update_idea_status'),
    # Admin Dashboard URLs
    path('ideas/<int:pk>/get-notes/', views.get_idea_notes, name='get_idea_notes'),
    path('ideas/<int:pk>/update-notes/', views.update_idea_notes, name='update_idea_notes'),
]
