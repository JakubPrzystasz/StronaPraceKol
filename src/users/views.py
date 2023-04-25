# forms
from django.contrib import messages
# to use user system
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
# for login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError
from django.core.mail import EmailMultiAlternatives
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
# for TemplateView classes
from django.views.generic import ListView, TemplateView
from StronaProjektyKol.settings import SITE_NAME, SITE_DOMAIN, SITE_ADMIN_MAIL, SITE_ADMIN_PHONE
from papers.models import Announcement, NotificationPeriod, Paper
# forms
from .forms import UserLoginForm, UserPasswordChangeForm
from .forms import UserRegisterForm
from .models import UserDetail


class IndexView(ListView):
    template_name = 'users/index.html'
    model = Announcement

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['site_name'] = 'index'
        context['site_title'] = f'Strona główna - {SITE_NAME}'
        context['announcement'] = Announcement.objects.filter(pk=1).first()
        return context


class SendNotificationsView(TemplateView):
    template_name = 'users/check_notifications.html'

    def send_notification(self):
        period = NotificationPeriod.objects.all().first().period
        for user in User.objects.all():
            userDetail = UserDetail.objects.filter(user=user).first()
            try:
                difference = timezone.now() - userDetail.last_seen
            except:
                continue

            if difference.seconds > period:
                papers = []

                for paper in Paper.objects.filter():
                    if user == paper.author or user in paper.reviewers.all():
                        messages = paper.get_unread_messages(user)
                        if len(messages) > 0:
                            papers.append((paper.title, messages, paper.pk))

                if len(papers) > 0 and not userDetail.email_notification_sent:
                    messages = []
                    for paper in papers:
                        messages.append(({'count': len(paper[1]), 'title': paper[0], 'id': paper[2]}))

                    userDetail.email_notification_sent = True
                    userDetail.save()

                    # now send an email
                    subject = f'Posiadasz nieprzeczytane wiadomości - {SITE_NAME}'
                    plaintext = loader.get_template('papers/paper_unseen_mail.html')
                    htmltemp = loader.get_template('papers/paper_unseen_mail.html')
                    c = {
                        'subject': subject,
                        'messages': messages,
                        'domain': SITE_DOMAIN,
                        'site_name': SITE_NAME,
                        'last_seen': userDetail.last_seen,
                        'protocol': 'https',
                    }
                    text_content = plaintext.render(c)
                    html_content = htmltemp.render(c)
                    try:
                        msg = EmailMultiAlternatives(subject, text_content, SITE_ADMIN_MAIL, [user.email],
                                                     headers={'Reply-To': SITE_ADMIN_MAIL})
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

    def get(self, request, *args, **kwargs):
        self.send_notification()
        return super(SendNotificationsView, self).get(request, *args, **kwargs)


class ContactView(ListView):
    template_name = 'users/index.html'
    model = Announcement

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['site_name'] = 'contact'
        context['site_title'] = f'Kontakt - {SITE_NAME}'
        context['announcement'] = Announcement.objects.filter(pk=2).first()
        return context


class RegisterView(TemplateView):
    template_name = 'users/register.html'

    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        # Call the base implementation first to get the context
        context = super(RegisterView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context = {
            'form': form,
            'site_name': 'register',
            'site_title': f'Rejestracja - {SITE_NAME}'
        }
        # Check if user is already logged
        if (self.request.user.is_authenticated):
            return redirect('index')
        else:
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            form = UserRegisterForm(self.request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(self.request, f'Konto zostało utworzone dla {username}')
                return redirect('login')
            else:
                return render(request, self.template_name, {'form': form})
        return render(request, self.template_name, {'form': UserRegisterForm()})


class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        # Check if user is already logged
        if self.request.user.is_authenticated:
            form = UserLoginForm()
            return redirect('index')
        else:
            form = UserLoginForm()
            context = {
                'form': form,
                'site_name': 'login',
                'site_title': f'Logowanie - {SITE_NAME}'
            }
            return render(request, self.template_name, context)


class LogoutView(auth_views.LogoutView):
    template_name = 'users/logout.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LogoutView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['site_name'] = 'logout'
        context['site_title'] = f'Wylogowano - {SITE_NAME}'
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, then redirect
    # redirect_field_name = 'login' # if user isn't logged, when redirect

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['site_name'] = 'profile'
        context['site_title'] = f'Ustawienia konta - {SITE_NAME}'
        context['userdetail']=UserDetail.objects.get(user=self.request.user) 
        # Additional info about living place /\ /\
        return context


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, when redirect
    template_name = 'users/passwordChange.html'

    def get(self, request, *args, **kwargs):
        form = UserPasswordChangeForm(self.request.user)
        # Call the base implementation first to get the context
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context = {
            'form': form,
            'site_name': 'password_change',
            'site_title': f'Zmiana hasła - {SITE_NAME}'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            form = UserPasswordChangeForm(self.request.user, self.request.POST)
            if form.is_valid():
                form.save()
                messages.success(self.request, f'Hasło zostało zmienione')
                return redirect('profile')
        else:
            form = UserPasswordChangeForm(self.request.user)
        return render(request, self.template_name, {'form': form})


class AccountDeleteView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, then redirect to login page
    template_name = 'users/accountDelete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AccountDeleteView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['site_name'] = 'account_delete'
        context['site_title'] = f'Usuwanie konta - {SITE_NAME}'
        return context

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            request.user.delete()
            messages.success(self.request, f'Konto zostało usunięte')
            return redirect('index')

        return render(request, self.template_name)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                user = associated_users.first()
                subject = f'Odzyskiwanie hasła - {SITE_NAME}'
                plaintext = loader.get_template('registration/password_reset_email.txt')
                htmltemp = loader.get_template('registration/password_reset_email.html')
                c = {
                    'subject': subject,
                    'email': user.email,
                    'username': user.username,
                    'domain': SITE_DOMAIN,
                    'site_name': SITE_NAME,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https',
                }
                text_content = plaintext.render(c)
                html_content = htmltemp.render(c)
                try:
                    msg = EmailMultiAlternatives(subject, text_content, SITE_ADMIN_MAIL, [user.email],
                                                 headers={'Reply-To': SITE_ADMIN_MAIL})
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect('password_reset_done')
            else:
                messages.add_message(request, messages.WARNING,
                                     'Nie znaleziono konta powiązanego z podanym adresem email')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset_form.html",
                  context={"form": password_reset_form})
