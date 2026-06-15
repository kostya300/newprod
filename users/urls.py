# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [

    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(template_name='store/login.html'), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/delete/', views.DeleteProfileView.as_view(), name='delete_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    # 🔐 Сброс пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/users/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/users/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

]
