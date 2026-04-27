# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Profile # Add Profile
from django.contrib import messages
import os # For deleting old profile picture if needed
from django.conf import settings # To get MEDIA_ROOT

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        error_messages = []
        if not username: error_messages.append("Username is required.")
        if not email: error_messages.append("Email is required.")
        if not password: error_messages.append("Password is required.")
        if password != password_confirm: error_messages.append("Passwords do not match.")
        if User.objects.filter(username=username).exists(): error_messages.append("Username already taken.")
        if User.objects.filter(email=email).exists(): error_messages.append("Email already registered.")

        if not error_messages:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                messages.success(request, "Registration successful! Welcome.")
                return redirect('home')
            except Exception as e:
                error_messages.append(f"An error occurred: {e}")
        
        for error in error_messages:
            messages.error(request, error)
        return render(request, 'core/register.html', {'input_values': request.POST}) # Pass back input values

    return render(request, 'core/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            next_url = request.GET.get('next') # For redirecting after login if 'next' param is present
            return redirect(next_url or 'home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'core/login.html', {'username': username})

    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')



# @login_required
# def home_view(request):
#     posts = Post.objects.all().select_related('user__profile') \
#                               .prefetch_related('comments__user__profile', 'likes')
#     # Added __profile to user for easier access and prefetch 'likes'
#     return render(request, 'core/home.html', {'posts': posts})



# @login_required # Keep home page login required for this design
# def home_view(request):
#     search_query = request.GET.get('search_user', '').strip()
    
#     posts_queryset = Post.objects.all().select_related('user__profile') \
#                                    .prefetch_related('comments__user__profile', 'likes')
    
#     searched_user_info = None # To display info about the user being searched

#     if search_query:
#         # Search for users whose username contains the query
#         # We'll display posts from the first match if multiple users have similar names.
#         # For a more robust search, you might want to list matching users first.
#         try:
#             # Exact match for simplicity first, or you can use .filter(username__icontains=search_query)
#             target_user = User.objects.get(username__iexact=search_query) 
#             posts_queryset = posts_queryset.filter(user=target_user)
#             searched_user_info = target_user
#             if not posts_queryset.exists():
#                 messages.info(request, f"No posts found for user '{target_user.username}'.")
#         except User.DoesNotExist:
#             messages.error(request, f"User '{search_query}' not found.")
#             # Optionally, show all posts or an empty list if user not found
#             # posts_queryset = Post.objects.none() # Show no posts if user not found
    
#     context = {
#         'posts': posts_queryset,
#         'search_query': search_query, # Pass the query back to prefill the search box
#         'searched_user_info': searched_user_info
#     }
#     return render(request, 'core/home.html', context)


# core/views.py
# ... other imports ...
from django.db.models import Q

@login_required
def home_view(request):
    search_query = request.GET.get('search_user', '').strip()
    
    # Start with all posts, then filter if needed
    posts_queryset = Post.objects.all().select_related('user__profile') \
                                   .prefetch_related('comments__user__profile', 'likes')
    
    searched_user_info = None 

    if search_query:
        try:
            # Using iexact for a direct username match.
            # For a broader search, consider username__icontains
            target_user = User.objects.get(username__iexact=search_query)
            posts_queryset = posts_queryset.filter(user=target_user)
            searched_user_info = target_user
            if not posts_queryset.exists(): # If user exists but has no posts
                messages.info(request, f"User '{target_user.username}' hasn't posted anything yet.")
        except User.DoesNotExist:
            messages.error(request, f"User '{search_query}' not found. Showing all recent posts instead.")
            # When user not found, we will fall back to showing all posts (the initial posts_queryset)
            # Alternatively, to show nothing:
            # posts_queryset = Post.objects.none() 
            # searched_user_info will remain None
            search_query = "" # Clear search_query so template doesn't think a successful search happened for a non-existent user
    
    context = {
        'posts': posts_queryset,
        'search_query': search_query, 
        'searched_user_info': searched_user_info
    }
    return render(request, 'core/home.html', context)

@login_required
def profile_view(request):
    user_posts = Post.objects.filter(user=request.user).prefetch_related('comments__user')
    return render(request, 'core/profile.html', {'user_posts': user_posts})

@login_required
def add_post_view(request):
    if request.method == 'POST':
        caption = request.POST.get('caption', '').strip()
        audio_file = request.FILES.get('audio_file')

        error_messages = []
        if not audio_file:
            error_messages.append("Audio file is required.")
        else:
            # Basic validation for audio file type (you can extend this)
            if not audio_file.name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                error_messages.append("Invalid audio file format. Please upload MP3, WAV, OGG, or M4A.")
            # Basic size validation (e.g., 10MB limit)
            if audio_file.size > 10 * 1024 * 1024: # 10 MB
                error_messages.append("Audio file is too large (max 10MB).")
        
        if not error_messages:
            try:
                Post.objects.create(user=request.user, caption=caption, audio_file=audio_file)
                messages.success(request, "Post added successfully!")
                return redirect('home')
            except Exception as e:
                error_messages.append(f"An error occurred while saving: {e}")
        
        for error in error_messages:
            messages.error(request, error)
        return render(request, 'core/add_post.html', {'caption': caption}) # Pass back caption

    return render(request, 'core/add_post.html')

@login_required
def add_comment_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_text = request.POST.get('comment_text', '').strip()

        if comment_text:
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            messages.success(request, "Comment added.")
        else:
            messages.error(request, "Comment cannot be empty.")
        
        # Redirect to the home page, or ideally, to the part of the page where the post is
        # Using a fragment identifier can help: return redirect(f"{reverse('home')}#post-{post_id}")
        return redirect('home') 
    return redirect('home') # Or handle GET requests differently if needed



@login_required
def profile_view(request):
    user = request.user
    profile = user.profile 
    user_posts = Post.objects.filter(user=user) \
                             .select_related('user__profile') \
                             .prefetch_related('comments__user__profile', 'likes')
    # Added __profile to user for easier access and prefetch 'likes'

    # ... (rest of the profile update logic from previous step) ...
    # (Make sure the context dictionary for both GET and POST error cases includes 'profile')
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        profile_image_file = request.FILES.get('profile_image')

        error_messages = []
        updated_fields_count = 0

        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                error_messages.append("Username already taken.")
            else:
                user.username = new_username
                updated_fields_count += 1
        
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                error_messages.append("Email already registered by another user.")
            else:
                user.email = new_email
                updated_fields_count += 1
        
        if updated_fields_count > 0 and not error_messages:
            try:
                user.save()
            except Exception as e:
                 error_messages.append(f"Error updating user details: {e}")

        if profile_image_file:
            allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
            if not profile_image_file.name.lower().endswith(allowed_extensions):
                error_messages.append(f"Invalid image format. Allowed: {', '.join(allowed_extensions)}.")
            elif profile_image_file.size > 2 * 1024 * 1024: 
                error_messages.append("Image file is too large (max 2MB).")
            else:
                if profile.image and profile.image.name != 'profile_pics/default.jpg':
                    old_image_path = os.path.join(settings.MEDIA_ROOT, profile.image.name)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception as e:
                            print(f"Error deleting old profile image: {e}") 

                profile.image = profile_image_file
                # updated_fields_count += 1 # This line was causing double count, image change handled by profile.save()
        
        profile_changed_or_user_updated = (updated_fields_count > 0 or profile_image_file)

        if profile_changed_or_user_updated and not error_messages:
            try:
                if profile_image_file: # Only save profile if image changed
                    profile.save() 
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
            except Exception as e:
                error_messages.append(f"Error saving profile: {e}")
        elif not error_messages and not profile_changed_or_user_updated:
             messages.info(request, "No changes were made.")
        
        for error in error_messages:
            messages.error(request, error)
        
        context = {
            'user_posts': user_posts,
            'profile': profile,
            'current_username': new_username or user.username,
            'current_email': new_email or user.email,
        }
        return render(request, 'core/profile.html', context)

    context = {
        'user_posts': user_posts,
        'profile': profile, 
        'current_username': user.username,
        'current_email': user.email,
    }
    return render(request, 'core/profile.html', context)


@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST': # Ensure it's a POST request for safety
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            # messages.info(request, "You unliked the post.") # Optional message
        else:
            post.likes.add(request.user)
            # messages.success(request, "You liked the post.") # Optional message
    
    # Redirect back to the page the user came from, or home as a fallback
    # Using HTTP_REFERER can be a bit unreliable, but often works well.
    # For a more robust solution on complex pages, you might pass a 'next' parameter.
    redirect_url = request.META.get('HTTP_REFERER', 'home')
    return redirect(redirect_url)