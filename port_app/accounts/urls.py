from django.conf.urls import url, patterns
from .views import *

urlpatterns = [
    url(r'^dashboard/$', Dashboard.as_view(), name='dashboard'),

    # url(r'^create-account/$', CreateAccountView.as_view(), name='registration'),
    url(r'^user-registration/$', UserRegistration.as_view(), name='user-registration'),
    url(r'^user-registration-done/$', UserRegistrationDone.as_view(), name='user-registration-done'),
    url(r'^user-registration-confirm/$', UserRegistrationConfirmEmail.as_view(), name='user-registration-confirm'),

    url(r'^confirm/$', confirm, name='confirm'),

    url(r'^test/$', TestView.as_view(), name='test'),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^user-login/$', UserLoginView.as_view(), name='user-login'),

    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    url(r'^user-logout/$', UserLogOutView.as_view(), name='user-logout'),

    url(r'^users/$', UserListView.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', UserUpdateView.as_view(), name='user-detail'),

    url(r'^profile-update/$', SelfProfileUpdateView.as_view(), name='profile-update'),

    url(r'^agents/$', AgentListView.as_view(), name='agent-list'),
    url(r'^agents/add/$', AgentCreateView.as_view(), name='agent-add'),
    url(r'^agents/(?P<pk>[0-9]+)/$', AgentUpdateView.as_view(), name='agent-detail'),

    url(r'^password-change/$', PasswordChangeView.as_view(),
        name='password-change'),

    url(r'^user-password-change/$', UserPasswordChangeView.as_view(),
        name='user-password-change'),

    url(r'^password-change-done/$', PasswordChangeDoneView.as_view(),
        name='password_change_done'),
    url(r'^password-reset/$', PasswordResetView.as_view(),
        name='password-reset'),

    url(r'^user-password-reset/$', UserPasswordResetView.as_view(),
        name='user-password-reset'),

    url(r'^password-reset-done/$', PasswordResetDoneView.as_view(),
        name='password-reset-done'),

    url(r'^user-password-reset-done/$', UserPasswordResetDoneView.as_view(),
        name='user-password-reset-done'),

    url(r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$',
        PasswordResetConfirmView.as_view(),  # NOQA
        name='password-reset-confirm'),

    url(r'^user-password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$',
        UserPasswordResetConfirmView.as_view(),  # NOQA
        name='user-password-reset-confirm'),

]
