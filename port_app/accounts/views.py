from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, FormView, View, RedirectView, TemplateView, ListView, DetailView, \
    UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from .forms import *
from .tools import *
from .tasks import *
from booking.utils.tools import get_or_none
from booking.models import *
from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth.views import password_reset, password_reset_done
# from django.contrib.auth.forms import PasswordResetForm
from authtools import views as authviews
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from braces.views import LoginRequiredMixin
from booking.models import Booking
from port_app.permissions import *

User = get_user_model()


class TestView(TemplateView):
    """
        Home page static view
    """
    # template_name = "user/layout.html"
    # template_name = "user/table.html"
    template_name = "accounts/admin_port/dashboard.html"
    # template_name = "accounts/admin/agency.html"
    # template_name = "accounts/admin/add-agency.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_user:
            return redirect(reverse("accounts:profile-update"))


class UserRegistrationDone(TemplateView):
    template_name = "accounts/user_port/registration_done.html"


class UserRegistrationConfirmEmail(TemplateView):
    template_name = "accounts/user_port/registration_confirm_email.html"


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin_port/dashboard.html"
    login_url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        if request.user.is_user:
            return redirect(reverse("accounts:profile-update"))
        else:
            return super(Dashboard, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        user_count = User.objects.filter(groups__name='user').count()
        agent_count = User.objects.filter(groups__name='agent').count()
        booking_count = Booking.objects.all().count()
        context['user_count'] = user_count
        context['agent_count'] = agent_count
        context['booking_count'] = booking_count
        d = {}
        l = []
        for vessel in Vessel.objects.all():
            d['num'] = vessel.mmsi
            d['title'] = vessel.name
            l.append(d)
            d = {}
        context['vessels'] = l
        return context


# Agent create
class CreateAccountView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/admin_port/signup.html"
    success_url = '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponse("Login olub")
        return super(CreateAccountView, self).get(request, *args, **kwargs)


# User registration
class UserRegistration(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/user_port/signup.html"
    success_url = reverse_lazy("accounts:user-registration-confirm")

    def get_context_data(self, **kwargs):
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        return super(UserRegistration, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("accounts:profile-update"))
        return super(UserRegistration, self).get(request, *args, **kwargs)


class LoginView(FormView):
    form_class = MyAuthenticationForm
    # success_url = reverse_lazy('home')
    template_name = 'accounts/admin_port/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("accounts:dashboard"))
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url:
            if next_url == reverse_lazy("accounts:logout"):
                return reverse("accounts:dashboard")
            return next_url
        else:
            # if self.request.user.is_user:
            #     return reverse("accounts:profile-update")
            # elif self.request.user.is_superuser:
            return reverse("accounts:dashboard")

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(email=username, password=password)

        if not user.is_user:
            if user is not None and user.is_active:
                login(self.request, user)
                return super(LoginView, self).form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class UserLoginView(FormView):
    form_class = MyAuthenticationForm
    template_name = 'accounts/user_port/login.html'
    group_required = u"user"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("booking:user-overview"))
        return super(UserLoginView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url:
            if next_url == reverse_lazy("accounts:logout") or next_url == reverse_lazy("accounts:user-logout"):
                return reverse_lazy("booking:user-overview")
            return next_url
        else:
            return reverse_lazy("booking:user-overview")

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(email=username, password=password)

        if user.is_user:
            login(self.request, user)
            return super(UserLoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)


class LogOutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("accounts:login")
    login_url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)


class UserLogOutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('accounts:user-login')
    login_url = reverse_lazy("accounts:user-login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(UserLogOutView, self).get(request, *args, **kwargs)


class PasswordChangeView(LoginRequiredMixin, authviews.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/admin_port/password-change.html'
    success_url = reverse_lazy("accounts:dashboard")
    login_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super(PasswordChangeView, self).form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, authviews.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/user_port/password-change.html'
    success_url = reverse_lazy("accounts:profile-update")
    login_url = reverse_lazy("accounts:user-login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super(UserPasswordChangeView, self).form_valid(form)


class PasswordChangeDoneView(authviews.LoginRequiredMixin, TemplateView):
    template_name = 'accounts/admin_port/password_change_done.html'
    login_url = reverse_lazy("accounts:login")


class PasswordResetView(authviews.PasswordResetView):
    form_class = PasswordResetForm
    domain_override = settings.HOST
    template_name = 'accounts/admin_port/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/password-reset-email.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponse("Login olub")
        return super(PasswordResetView, self).get(request, *args, **kwargs)


class UserPasswordResetView(authviews.PasswordResetView):
    form_class = PasswordResetForm
    domain_override = settings.HOST
    template_name = 'accounts/user_port/password-reset.html'
    success_url = reverse_lazy('accounts:user-password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/user-password-reset-email.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("accounts:profile-update"))
        return super(UserPasswordResetView, self).get(request, *args, **kwargs)


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/admin_port/password-reset-done.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponse("Login olub")
        return super(PasswordResetDoneView, self).get(request, *args, **kwargs)


class UserPasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/user_port/password-reset-done.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("accounts:profile-update"))
        return super(UserPasswordResetDoneView, self).get(request, *args, **kwargs)


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'accounts/admin_port/password-reset-confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy("accounts:dashboard")


class UserPasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'accounts/user_port/password-reset-confirm.html'
    form_class = SetPasswordForm


class UserListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = User
    paginate_by = 25
    template_name = "accounts/admin_port/user_list.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("accounts.user_all_view", ),
    }

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        queryset = self.model.objects.filter(groups__name='user')
        if q:
            if q.isdigit():
                query = Q(email__icontains=q) | Q(first_name__icontains=q) \
                        | Q(first_name__icontains=q) | Q(pk=q)
                queryset = queryset.filter(query)
                return queryset
            else:
                query = Q(email__icontains=q) | Q(first_name__icontains=q) \
                        | Q(first_name__icontains=q)
                queryset = queryset.filter(query)
                return queryset
        else:
            return queryset


class UserUpdateView(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/admin_port/update-profile.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("accounts.user_super_create", ),
    }


class SelfProfileUpdateView(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = User
    form_class = SelfUserUpdateForm
    template_name = "accounts/user_port/update_profile.html"
    login_url = reverse_lazy("accounts:user-login")
    success_url = reverse_lazy("accounts:profile-update")

    permissions = {
        "all": ("accounts.user_view", ),
    }

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.user.pk)


class AgentListView(LoginRequiredMixin, ListView, MultiplePermissionsMixin):
    model = Agent
    paginate_by = 25
    template_name = "accounts/admin_port/agency-list.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("accounts.agent_all_view", ),
    }

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        if q:
            query = Q(owner__email__icontains=q) | Q(name__icontains=q)
            queryset = self.model.objects.filter(query)
            return queryset
        else:
            return super(AgentListView, self).get_queryset()


class AgentCreateView(LoginRequiredMixin, CreateView, MultiplePermissionsMixin):
    template_name = 'accounts/admin_port/add-agency.html'
    model = User
    form_class = MyUserCreationForm
    success_url = reverse_lazy("accounts:agent-list")

    permissions = {
        "all": ("accounts.user_super_create", "accounts.add_agent"),
    }

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        agent_form_set = AgentFormSet()

        return self.render_to_response(
            self.get_context_data(form=form,
                                  agent_form_set=agent_form_set,))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        agent_form_set = AgentFormSet(request.POST)
        if form.is_valid() and agent_form_set.is_valid():
            return self.form_valid(form, agent_form_set)
        else:
            return self.form_invalid(form, agent_form_set)

    def form_valid(self, form, agent_form_set,):
        group_agent = get_or_none(Group, name='agent')
        self.object = form.save(commit=False)
        self.object.is_active = True
        self.object.save()
        self.object.groups.add(group_agent)
        agent_form_set.instance = self.object
        agent_form_set.save()
        # balance = Balance(owner=self.object, amount=0)
        # balance.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, agent_form_set):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  agent_form_set=agent_form_set))


class AgentUpdateView(LoginRequiredMixin, UpdateView, MultiplePermissionsMixin):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/admin_port/agency.html"
    login_url = reverse_lazy("accounts:login")

    permissions = {
        "all": ("accounts.change_agent", ),
    }

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        agent_form_set = AgentFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(
            form=form,
            agent_form_set=agent_form_set,
            object=self.object
        ))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        agent_form_set = AgentFormSet(request.POST, instance=self.object)
        if form.is_valid() and agent_form_set.is_valid():
            return self.form_valid(form, agent_form_set)
        else:
            return self.form_invalid(form, agent_form_set)

    def form_valid(self, form, agent_form_set):
        self.object = form.save()
        agent_form_set.save()
        return redirect(reverse('accounts:agent-detail', kwargs={'pk': self.object.pk}))

    def form_invalid(self, form, agent_form_set):
        return self.render_to_response(self.get_context_data(form=form, agent_form_set=agent_form_set))


def confirm(request):
    try:
        activation_key = django_forms.CharField().clean(request.GET.get("activation"))
        confirm_user = User.objects.get(activation_key=activation_key)
        if confirm_user.is_active:
            return HttpResponseForbidden()

        if confirm_user.expiration_date > timezone.now():
            confirm_user.is_active = True
            confirm_user.save()
            group_user = get_or_none(Group, name='user')
            confirm_user.groups.add(group_user)
            return redirect(reverse("accounts:user-registration-done"))
        else:
            raise ValueError()

    except (User.DoesNotExist, ValueError, django_forms.ValidationError):
        return HttpResponseBadRequest()
