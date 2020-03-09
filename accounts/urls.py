from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy, include
from . import views

app_name = 'accounts'
urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),

    # login - logout urls
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout_then_login/', auth_views.logout_then_login, name='logout_then_login'),

    # Change password urls
    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),

    # restore password urls
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('', include('django.contrib.auth.urls')),

    # user profiles
    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<username>/', views.user_detail, name='user_detail'),

]
