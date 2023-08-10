from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from PIL import Image

# Models created -  Database
class Expense(models.Model):
    expense_name = models.CharField(max_length=50)
    date_created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey('Group', default=1, on_delete=models.CASCADE)
    users_paid_for = models.ManyToManyField(get_user_model(), related_name='expenses_paid_for')

class Group(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField(get_user_model(), related_name='participant_groups', blank=True)
    group_name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)


def get_default_user():
    return get_user_model().objects.get(username='default_username')  # Replace 'default_username' with the actual default username

class Participant(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
