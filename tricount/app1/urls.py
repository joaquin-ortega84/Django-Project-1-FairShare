from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path('register/',views.register, name='register'),
    path("main/", views.main, name="main"),
    path("profile/", views.profile, name="profile"),
    path("create_group/", views.create_group, name="create_group"),
    path("new_expense/", views.new_expense, name="new_expense"),
    path('group/<int:group_id>/expenses/', views.group_expenses, name='group_expenses'),

    # Login and Logout
    path("login/", auth_views.LoginView.as_view(template_name='app1/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='app1/logout.html'), name="logout"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
pass
