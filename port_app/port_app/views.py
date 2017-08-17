from django.views.generic.base import TemplateView
from accounts.forms import MyAuthenticationForm
from booking.forms import BookingInitialForm
from django.shortcuts import redirect



def home_red(request):
    return redirect('booking:user-booking')




class HomePageView(TemplateView):
    """
        Home page of site
    """
    template_name = "user_port/main.html"

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        kwargs['login_form'] = MyAuthenticationForm(self.request)
        kwargs['booking_form'] = BookingInitialForm()

        return super(HomePageView, self).get_context_data(**kwargs)


class LoginView(TemplateView):
    """
        Home page static view
    """
    template_name = "admin_port/layout-login.html"

