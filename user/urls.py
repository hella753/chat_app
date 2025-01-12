from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from user import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name="authorization/login.html"
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="password-reset/reset-password.html",
        email_template_name='reset-password-email.html',
    success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name="password-reset/reset-password-done.html"
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="password-reset/reset-password-confirm.html",
        success_url=reverse_lazy('accounts:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="password-reset/reset-password-complete.html"
    ), name='password_reset_complete'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', TemplateView.as_view(template_name='authorization/verify.html'), name='verify'),
    path('my-profile/', views.MyProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('my-profile/<str:username>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('my-profile/<str:username>/update/password/', views.ProfileUpdatePasswordView.as_view(), name='profile_update_password'),
    path('activate/<int:uid>/<str:token>/', views.VerificationView.as_view(), name='activate'),
    # path('page-not-found/', views.PageNotFound.as_view(), name='page_not_found'),
    # path('server-error/', views.InternalServerError.as_view(), name='server_error'),
]
