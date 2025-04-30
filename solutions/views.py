from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Idea, Category, Vote, Comment
from .forms import IdeaForm, CommentForm
import json

def is_admin(user):
    return user.is_staff or user.is_superuser

def home(request):
    latest_ideas = Idea.objects.select_related('category', 'author').prefetch_related('vote_set').order_by('-created_at')[:6]
    categories = Category.objects.annotate(idea_count=Count('idea')).order_by('name')
    return render(request, 'solutions/home.html', {
        'latest_ideas': latest_ideas,
        'categories': categories,
    })

def idea_list(request):
    category_id = request.GET.get('category')
    if category_id:
        ideas = Idea.objects.filter(category_id=category_id)
    else:
        ideas = Idea.objects.all()
    
    ideas = ideas.annotate(vote_count=Count('vote')).order_by('-vote_count')
    return render(request, 'solutions/idea_list.html', {'ideas': ideas})

@login_required
def idea_create(request):
    if request.method == 'POST':
        # Handle form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        idea = Idea.objects.create(
            title=title,
            description=description,
            category_id=category_id,
            author=request.user,
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        messages.success(request, 'Your idea has been submitted successfully!')
        return redirect('solutions:idea_detail', pk=idea.pk)
    
    categories = Category.objects.all()
    return render(request, 'solutions/idea_form.html', {'categories': categories})

def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    comments = idea.comment_set.all().order_by('-created_at')
    user_has_voted = False
    if request.user.is_authenticated:
        user_has_voted = Vote.objects.filter(user=request.user, idea=idea).exists()
    
    context = {
        'idea': idea,
        'comments': comments,
        'user_has_voted': user_has_voted,
    }
    return render(request, 'solutions/idea_detail.html', context)

@login_required
def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if idea.author != request.user:
        messages.error(request, "You can't edit this idea.")
        return redirect('solutions:idea_detail', pk=pk)
    
    if request.method == 'POST':
        # Handle form submission
        idea.title = request.POST.get('title')
        idea.description = request.POST.get('description')
        idea.category_id = request.POST.get('category')
        idea.location = request.POST.get('location')
        idea.latitude = request.POST.get('latitude')
        idea.longitude = request.POST.get('longitude')
        idea.save()
        
        messages.success(request, 'Your idea has been updated successfully!')
        return redirect('solutions:idea_detail', pk=pk)
    
    categories = Category.objects.all()
    return render(request, 'solutions/idea_form.html', {
        'idea': idea,
        'categories': categories,
    })

@login_required
def idea_vote(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    vote, created = Vote.objects.get_or_create(user=request.user, idea=idea)
    
    if not created:
        vote.delete()
        action = 'removed'
    else:
        action = 'added'
    
    vote_count = idea.vote_set.count()
    return JsonResponse({'action': action, 'votes': vote_count})

@login_required
def add_comment(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                idea=idea,
                author=request.user,
                content=content
            )
            messages.success(request, 'Your comment has been added successfully!')
        return redirect('solutions:idea_detail', pk=pk)
    return redirect('solutions:idea_detail', pk=pk)

@login_required
def profile(request):
    user_ideas = Idea.objects.filter(author=request.user)
    voted_ideas = Idea.objects.filter(vote__user=request.user)
    context = {
        'user_ideas': user_ideas,
        'voted_ideas': voted_ideas,
    }
    return render(request, 'solutions/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'solutions/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Get all ideas with vote counts
    ideas = Idea.objects.annotate(vote_count=Count('vote')).order_by('-vote_count')
    
    # Get statistics
    total_ideas = ideas.count()
    implemented_count = ideas.filter(implementation_status='completed').count()
    in_progress_count = ideas.filter(implementation_status='in_progress').count()
    pending_count = ideas.filter(implementation_status='pending').count()
    
    # Get category distribution
    categories = Category.objects.annotate(idea_count=Count('idea'))
    category_labels = [cat.name for cat in categories]
    category_data = [cat.idea_count for cat in categories]
    
    # Get status distribution
    status_counts = {
        'Pending': pending_count,
        'In Progress': in_progress_count,
        'Completed': implemented_count,
        'Rejected': ideas.filter(implementation_status='rejected').count()
    }
    status_labels = list(status_counts.keys())
    status_data = list(status_counts.values())
    
    # Get top ideas (most voted)
    top_ideas = ideas[:10]  # Get top 10 ideas
    
    context = {
        'total_ideas': total_ideas,
        'implemented_count': implemented_count,
        'in_progress_count': in_progress_count,
        'pending_count': pending_count,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'top_ideas': top_ideas,
    }
    
    return render(request, 'solutions/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_idea_status(request, pk):
    if request.method == 'POST':
        try:
            idea = get_object_or_404(Idea, pk=pk)
            idea.implementation_status = request.POST.get('status')
            idea.admin_notes = request.POST.get('notes')
            implementation_date = request.POST.get('implementation_date')
            if implementation_date:
                idea.implementation_date = implementation_date
            idea.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@user_passes_test(is_admin)
def get_idea_notes(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    return JsonResponse({
        'notes': idea.admin_notes,
        'implementation_date': idea.implementation_date.isoformat() if idea.implementation_date else None
    })

@user_passes_test(is_admin)
def update_idea_notes(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        idea = get_object_or_404(Idea, pk=pk)
        data = json.loads(request.body)

        idea.admin_notes = data.get('notes', '')
        implementation_date = data.get('implementation_date')
        if implementation_date:
            idea.implementation_date = implementation_date
        idea.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
