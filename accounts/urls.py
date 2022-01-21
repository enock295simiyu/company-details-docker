from django.contrib.auth import views as auth_views
from django.urls import path, include

from accounts import views
from accounts.views import EmailVerificationView, ProfileView, SendConfirmationTextView

urlpatterns = [
    path('create/', views.AccountCreation.as_view(), name='create_account'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogOutView.as_view(), name='logout'),
    path('password_reset/<int:id>/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_staff_list/', views.EmployeeListPasswordReset.as_view(), name='password_reset_staff_list'),
    path('activate/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='activate'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('send-verification-code/', SendConfirmationTextView.as_view(), name='send_verification_code'),
    path('accounts/', include('allauth.urls')),
    path("password-reset", auth_views.PasswordResetView.as_view(template_name="password_reset_client.html"),
         name="password_reset_client"),
    path("password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
         name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>",
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("password-reset-complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
         name="password_reset_complete")
]
