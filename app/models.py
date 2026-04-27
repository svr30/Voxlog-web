# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# class Post(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
#     caption = models.CharField(max_length=255, blank=True, null=True)
#     audio_file = models.FileField(upload_to='audio_posts/')
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Post by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

#     class Meta:
#         ordering = ['-created_at']



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.CharField(max_length=255, blank=True, null=True)
    audio_file = models.FileField(upload_to='audio_posts/')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True) # New field

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']

    @property
    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post_id}"

    class Meta:
        ordering = ['created_at']



from django.db.models.signals import post_save # Import post_save
from django.dispatch import receiver # Import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

# Signal to create or update the user profile automatically
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # This handles cases where an existing user might not have a profile yet
        # (e.g., if you add this feature to an existing project)
        Profile.objects.create(user=instance)