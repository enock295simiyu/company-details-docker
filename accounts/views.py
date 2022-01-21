import pytz
from babel._compat import force_text
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
# Create your views here.
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

from accounts.accounts_handler import AccountsHandler
from accounts.forms import SignUpFormClient, UpdateUserInformationForm
from accounts.forms import SingUpForm
from accounts.token import account_activation_token
from accounts.verify import send_code, check_code
from company_details.settings import TIME_ZONE
from core.core_handler import CoreHandler
from payment.payment_handler import PaymentHandler
from reports.reports_handler import ReportsHandler

tz = pytz.timezone(TIME_ZONE)


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AccountCreation(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.accounts_obj = AccountsHandler()
        self.core_obj = CoreHandler()

    def get(self, request, *args, **kwargs):
        self.context_dict['form'] = SingUpForm()

        return render(request, 'create_account.html', self.context_dict)

    def post(self, request, *args, **kwargs):

        form = SingUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            user.is_active = True
            user.is_staff = True
            user_profile = user.profile
            user_profile.phone_number = data.get('phone_number')
            user_profile.save()
            user.save()

            messages.success(request, 'You have successfully created an account for ' + user.username)
            return redirect('home')
        else:

            messages.error(request, 'Please fix the errors below.')
            self.context_dict['form'] = form
            return render(request, 'create_account.html', self.context_dict)


class EmailVerificationView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()

    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
            return redirect('login')
        else:
            messages.error(request, 'Activation link is invalid!')
            return redirect('login')


class LoginView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()

    def get(self, request, *args, **kwargs):

        return render(request, 'loginv2.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember-me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, "Log in was successful")
            return redirect(self.request.GET.get('next', 'profile'))

        else:

            messages.error(request, 'Please enter the correct username and password for a registered account. Note '
                                    'that '
                                    'both fields may be case-sensitive. ')
            return redirect('login')


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class LogOutView(View):
    def get(self, request):
        return render(request, 'logout.html')

    def post(self, request):
        logout(request)
        messages.success(request, 'You have successfully logged out. Log in again to use the site.')
        return redirect('login')


@method_decorator(login_required, name='post')
@method_decorator(login_required, name='get')
class PasswordResetView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.accounts_obj = AccountsHandler()
        self.core_obj = CoreHandler()

    def get(self, request, id, *args, **kwargs):
        return render(request, 'password_reset.html')

    def post(self, request, id, *args, **kwargs):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password2 != password1:
            messages.error(request, 'The first password does not match with the second password.')
            return redirect('password_reset', id=id)
        else:
            if len(password1) <= 7:
                messages.error(request, 'The password you provided is too short.')
                return redirect('password_reset', id=id)
            if password1.isdecimal():
                messages.error(request, 'The password you provided contains only numbers.')
                return redirect('password_reset', id=id)
            data = {
                'user_id': id
            }
            user = self.accounts_obj.get_user_by_id(data)
            try:
                user.set_password(password2)
                user.save()
                messages.success(request, 'You have successfully changed the password for ' + user.username + '.')
                return redirect('home')
            except:
                messages.error(request, 'An error occurred while changing the password. Please ensure the password you '
                                        'provided matches the guidelines shown below.')
                return redirect('password_reset', id=id)


@method_decorator(login_required, name='get')
class EmployeeListPasswordReset(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.accounts_obj = AccountsHandler()
        self.core_obj = CoreHandler()

    def get(self, request, *args, **kwargs):
        self.context_dict['all_staff'] = self.accounts_obj.get_all_staff()
        return render(request, 'password_reset_staff_list.html', self.context_dict)


class RegistrationView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.payment_obj = PaymentHandler()

    def get(self, request, *args, **kwargs):
        form = SignUpFormClient()
        self.context_dict['form'] = form
        return render(request, 'register.html', self.context_dict)

    def post(self, request, *args, **kwargs):
        form = SignUpFormClient(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            user.is_active = False
            user_profile = user.profile
            user_profile.phone_number = data.get('phone_number')
            user_profile.save()
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.info(request, 'Please confirm your email address to complete the registration')
            return redirect('login')
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            # messages.success(request, "Account creation was completed successfully")
            # return redirect('client_home')
        else:

            self.context_dict['form'] = form
            return render(request, 'register.html', self.context_dict)


@method_decorator(login_required, name='get')
class ProfileView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.accounts_obj = AccountsHandler()

    def get(self, request, *args, **kwargs):
        remaining_credits = PaymentHandler().return_users_remaining_credits({'user': request.user})
        self.context_dict['credits_remaining'] = remaining_credits
        self.context_dict['update_user_information_form'] = UpdateUserInformationForm(instance=request.user)
        self.context_dict['company_data_datewise'] = ReportsHandler().get_spend_credit_split_datewise(
            {'user': request.user})
        self.context_dict['user_report'] = ReportsHandler().get_user_report(
            {'daterange': request.GET.get('daterange'), 'page': request.GET.get('page', 1), 'user': request.user})
        return render(request, 'profile.html', self.context_dict)

    def post(self, request, *args, **kwargs):
        form = UpdateUserInformationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['user'] = request.user
            self.accounts_obj.update_user_information(data)
            messages.success(request,
                             'You have successfully updated your information.')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')
            remaining_credits = PaymentHandler().return_users_remaining_credits({'user': request.user})
            self.context_dict['credits_remaining'] = remaining_credits
            self.context_dict['update_user_information_form'] = UpdateUserInformationForm(request.POST)
            self.context_dict['update_info_tab'] = True
            return render(request, 'profile.html', self.context_dict)


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class SendConfirmationTextView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.accounts_obj = AccountsHandler()

    def get(self, request, *args, **kwargs):
        send_code(str(request.user.profile.phone_number))
        return JsonResponse({'data': 'Verification Code was send successfully'}, safe=False)

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        is_verified = check_code(str(request.user.profile.phone_number), code)
        if is_verified:
            self.accounts_obj.verify_phonenumber(request.user)
            messages.success(request, 'You have successfully verified your phone number')
            message = {'code': True, 'message': 'You have successfully verified your phone number'}
        else:
            message = {'code': False, 'message': 'The code you entered does not match the one that was send.'}
        return JsonResponse(message, safe=False)
