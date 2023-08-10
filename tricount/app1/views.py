from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app1.models import Group, Expense, Participant
from .forms import ExtendedUserCreationForm, UserUpdateForm
from .forms import ProfileUpdateForm, ParticipantForm, GroupForm  # Import your custom form from forms.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


# Views for app1
def home(request):
    return render(request, 'app1/home.html')

# Views for user registration
def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user instance to the database
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')  # Redirect to the 'login' URL name (your login page)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'app1/register.html', {'form': form})

# views.py

# views.py

from django.db.models import Sum

@login_required
def main(request):
    user = request.user
    groups = Group.objects.filter(owner=user) | Group.objects.filter(participants=user)

    for group in groups:
        # Check if the authenticated user is a participant in the group
        participant = group.participants.filter(user=user).first()
        if participant:
            # Calculate the participant's balance within this group
            expenses_paid_for = Expense.objects.filter(group=group, users_paid_for=user)
            total_expenses = expenses_paid_for.aggregate(Sum('amount'))['amount__sum'] or 0.0

            # Calculate total expenses paid by all participants in the group
            total_group_expenses = Expense.objects.filter(group=group).aggregate(Sum('amount'))['amount__sum'] or 0.0

            # Calculate the participant's share of expenses
            participant_share = total_group_expenses / group.participants.count()

            participant.balance = participant_share - total_expenses
            participant.save()

    context = {'groups': groups}
    return render(request, 'app1/main.html', context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # User with the provided email does not exist
            messages.error(request, 'User does not exist.')
            return render(request, 'login.html')  # Render the login form again with the error message

        user = authenticate(request, username=user.username)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

        # Check if the user has a profile before creating the form instance
        if hasattr(request.user, 'profile'):
            p_form = ProfileUpdateForm(instance=request.user.profile)
        else:
            p_form = ProfileUpdateForm()

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'app1/profile.html', context)

@login_required
def create_group(request):
    participant_form = ParticipantForm()

    if request.method == 'POST':
        # Get the form data for creating the group
        group_name = request.POST['group_name']
        description = request.POST['description']
        category = request.POST['category']
        currency = request.POST['currency']

        # Create the group instance
        group = Group.objects.create(group_name=group_name, description=description, category=category, currency=currency)

        # Initialize the GroupForm with POST data
        form = GroupForm(request.POST)

        if form.is_valid():
            # If the group form is valid, redirect to the main page
            return redirect('main')
        elif participant_form.is_valid():
            # If the participant form is valid, create a new participant instance
            participant_name = participant_form.cleaned_data['name']
            Participant.objects.create(group=group, name=participant_name, user=request.user)

            # Redirect back to the same page after adding participant
            return redirect('main')
    else:
        form = GroupForm()  # Initialize form without POST data

    context = {'form': form, 'participant_form': participant_form}
    return render(request, 'app1/create_group.html', context)




# views.py

def new_expense(request):
    groups = Group.objects.all()
    users = User.objects.all()

    if request.method == 'POST':
        expense_name = request.POST.get('expense_name')
        group_id = request.POST.get('group')
        author_id = request.POST.get('author')
        users_paid_for_ids = request.POST.getlist('users_paid_for')
        amount = float(request.POST.get('amount'))

        group = Group.objects.get(pk=group_id)
        author = User.objects.get(pk=author_id)
        users_paid_for = User.objects.filter(pk__in=users_paid_for_ids)

        expense = Expense.objects.create(
            expense_name=expense_name,
            group=group,
            author=author,
        )
        expense.users_paid_for.set(users_paid_for)

        # Distribute the expense amount among participants
        num_users = len(users_paid_for)
        individual_share = amount / num_users
        for user in users_paid_for:
            Participant.objects.get_or_create(group=group, name=user.username)
            participant = Participant.objects.get(group=group, name=user.username)
            participant.balance -= individual_share
            participant.save()

        Participant.objects.get_or_create(group=group, name=author.username)
        author_participant = Participant.objects.get(group=group, name=author.username)
        author_participant.balance += amount
        author_participant.save()

        return redirect('main')  # Redirect to expense list view

    return render(request, 'app1/new_expense.html', {'groups': groups, 'users': users})


@login_required
def group_expenses(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    expenses = Expense.objects.filter(group=group)

    context = {'group': group, 'expenses': expenses}
    return render(request, 'app1/group_expenses.html', context)


def group_list(request):
    user = request.user  # Get the logged-in user

    # Filter groups where the user is the owner or a participant who has accepted the invitation
    groups = Group.objects.filter(owner=user) | Group.objects.filter(participants=user)

    return render(request, 'app1/group_list.html', {'groups': groups})


def accept_invitation(request, group_id):
    group = Group.objects.get(pk=group_id)
    user = request.user

    group.participants.add(user)
    group.save()

    # Redirect to appropriate view

# Add a URL route for the accept_invitation view
