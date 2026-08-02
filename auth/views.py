from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True  

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('welcome')  # Redirige a la página de bienvenida
