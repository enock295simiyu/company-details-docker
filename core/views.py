# Create your views here.
import logging
import mimetypes
import ntpath
import traceback

from chunked_upload.views import ChunkedUploadCompleteView, ChunkedUploadView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from payment.payment_handler import PaymentHandler
from .core_handler import CoreHandler
from .filters import PeopleFilter
from .forms import CompanySourceFieldInputsMappingForm
from .manipulate_csv_file import CreateCSVReport, CSVJSON
from .models import MyChunkedUpload, CompanySource
from .scripts import VerifyEmail
from .tasks import populate_company_data_model_async


class ClientHome(TemplateView):
    template_name = 'client_index.html'

    def get_context_data(self, **kwargs):
        context = super(ClientHome, self).get_context_data(**kwargs)
        context['total_count_of_data'] = CoreHandler().return_all_data_count()
        context['credits_remaining'] = PaymentHandler().return_users_remaining_credits({'user': self.request.user})
        try:
            values = [p.organization_revenue_in_thousands_int for p in CompanySource.objects.all() if
                      p.organization_revenue_in_thousands_int is not None]
            min_value = min(values)
            max_value = max(values)
        except:
            min_value = 0
            max_value = 0
        context['min_value'] = min_value
        context['max_value'] = max_value
        context['company_data'] = CoreHandler().get_all_company_source_objects(
            {'page': 1, 'number-of-results-per-page': 10})
        context['total_number_of_pages'] = CoreHandler().get_page_metrics_for_all_company_data()
        return context


@login_required
def index(request):
    if not request.user.is_staff:
        messages.error(request, 'You are not permitted to access this page.')
        return redirect('client_home')
    context = {'total_count_of_data': CoreHandler().return_all_data_count(),
               'credits_remaining': PaymentHandler().return_users_remaining_credits({'user': request.user})}
    return render(request, 'index.html', context)


class ChunkedUploadDemo(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')
            return redirect('client_home')
        self.context_dict['credits_remaining'] = PaymentHandler().return_users_remaining_credits({'user': request.user})
        self.context_dict['upload_details_id'] = request.GET.get('upload_details_id')
        return render(request, 'chunked_upload_demo.html', self.context_dict)


class MyChunkedUploadView(ChunkedUploadView):
    model = MyChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')

            return login_required(login_url=reverse('login'))


class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()

    model = MyChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')
            return login_required(login_url=reverse('login'))

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)
        started_task = False
        core_obj = CoreHandler()
        json_file = core_obj.create_file({'json_file': uploaded_file})
        if request.POST.get('excel'):
            csv_json = CSVJSON(json_file.json_file.url[1:])
            json_file_path = csv_json.to_json()
            json_file = core_obj.add_json_file_to_file_object(
                {'json_file_id': json_file.id, 'json_file_path': json_file_path})
            task=populate_company_data_model_async.delay(
                {'json_file_id': json_file.id, 'upload_details_id': request.POST.get('upload_details_id')})
            core_obj.add_task_id_to_file({'file_id': json_file.id, 'task_id': task.id})
            started_task = True
        else:

            task=populate_company_data_model_async.delay(
                {'json_file_id': json_file.id, 'upload_details_id': request.POST.get('upload_details_id')})
            core_obj.add_task_id_to_file({'file_id': json_file.id, 'task_id': task.id})
            started_task = True

        self.context_dict['started_task'] = started_task

    def get_response_data(self, chunked_upload, request):
        if self.context_dict['started_task']:
            message = f'The upload was successful and the processing of the data has started. This might take sometime. ' \
                      f'You will be redirected the results page of started tasks. The size of data uploaded ' \
                      f'is "{chunked_upload.filename}" ({str(chunked_upload.offset)} bytes)! You will be redirected ' \
                      f'to the upload status page to view the status of your uploads'
        else:
            message = 'An error occurred and the file processing could not be started'

        return {'message': (message)}


@method_decorator(login_required, name='get')
class ViewCompanySourceSummaryListView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You are not permitted to access this page.')
            return redirect('client_home')
        addition_url_paramater = ''
        if request.GET.get('search-option') and request.GET.get('search-value'):
            self.context_dict['company_data'] = self.core_obj.filter_company_source_objects(
                {'page': request.GET.get('page', 1), 'search-option': request.GET.get('search-option'),
                 'search-value': request.GET.get('search-value'),
                 'number-of-results-per-page': request.GET.get('number-of-results-per-page'),
                 'order_by': request.GET.get('radio1')})
            addition_url_paramater = addition_url_paramater + 'search-option=' + str(
                request.GET.get('search-option')) + '&search-value=' + str(
                request.GET.get('search-value')) + '&' + 'number-of-results-per-page=' + str(
                request.GET.get('number-of-results-per-page')) + '&' + 'order_by=' + str(
                request.GET.get('radio1')) + '&'
        elif request.GET.get('search-option-seniority') and request.GET.get('search-value-seniority'):
            self.context_dict['company_data'] = self.core_obj.filter_company_source_objects_according_to_siniority(
                {'page': request.GET.get('page', 1), 'search-option': request.GET.get('search-option'),
                 'search-option-seniority': request.GET.get('search-option-seniority'),
                 'search-value': request.GET.get('search-value-seniority'),
                 'number-of-results-per-page': request.GET.get('number-of-results-per-page'),
                 'order_by': request.GET.get('radio1')})
            addition_url_paramater = addition_url_paramater + 'search-option=' + str(
                request.GET.get('search-option')) + '&search-value=' + str(
                request.GET.get('search-value')) + '&' + 'number-of-results-per-page=' + str(
                request.GET.get('number-of-results-per-page')) + '&' + 'order_by=' + str(
                request.GET.get('order_by')) + '&' + 'search-option-seniority=' + str(
                request.GET.get('search-option-seniority')) + '&'

        elif request.GET.get('person_location_country') and request.GET.get('search-value'):
            self.context_dict['company_data'] = self.core_obj.filter_company_source_objects_according_to_country(
                {'page': request.GET.get('page', 1), 'search-option': request.GET.get('search-option'),
                 'person_location_country': request.GET.get('person_location_country'),
                 'search-value': request.GET.get('search-value'),
                 'number-of-results-per-page': request.GET.get('number-of-results-per-page'),
                 'order_by': request.GET.get('radio1')})
            addition_url_paramater = addition_url_paramater + 'search-option=' + str(
                request.GET.get('search-option')) + '&search-value=' + str(
                request.GET.get('search-value')) + '&' + 'number-of-results-per-page=' + str(
                request.GET.get('number-of-results-per-page')) + '&' + 'order_by=' + str(
                request.GET.get('order_by')) + '&' + 'person_location_country=' + str(
                request.GET.get('person_location_country')) + '&'

        elif request.GET.get('search-value-min') and request.GET.get('search-value-max') and request.GET.get('search'
                                                                                                             '-value'):
            self.context_dict['company_data'] = self.core_obj.filter_company_source_objects_according_to_revenue_range(
                {'page': request.GET.get('page', 1), 'search-option': request.GET.get('search-option'),
                 'search-value-min': request.GET.get('search-value-min'),
                 'search-value-max': request.GET.get('search-value-max'),
                 'search-value': request.GET.get('search-value'),
                 'number-of-results-per-page': request.GET.get('number-of-results-per-page'),
                 'order_by': request.GET.get('radio1')})
            addition_url_paramater = addition_url_paramater + 'search-option=' + str(
                request.GET.get('search-option')) + '&search-value=' + str(
                request.GET.get('search-value')) + '&' + 'number-of-results-per-page=' + str(
                request.GET.get('number-of-results-per-page')) + '&' + 'order_by=' + str(
                request.GET.get('order_by')) + '&' + 'search-value-min=' + str(
                request.GET.get('search-value-min')) + '&' + 'search-value-max=' + str(
                request.GET.get('search-value-max')) + '&'

        else:
            self.context_dict['company_data'] = self.core_obj.get_all_company_source_objects(
                {'page': request.GET.get('page', 1)})
        self.context_dict['addition_url_paramater'] = addition_url_paramater
        self.context_dict['credits_remaining'] = PaymentHandler().return_users_remaining_credits({'user': request.user})
        return render(request, 'company_list.html', self.context_dict)


@method_decorator(login_required, name='get')
class ClientCompanyListView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request, *args, **kwargs):
        organisation_revenue_range = PeopleFilter(request.GET)
        try:
            values = [p.organization_revenue_in_thousands_int for p in CompanySource.objects.all() if
                      p.organization_revenue_in_thousands_int is not None]

            min_value = min(values)
            max_value = max(values)
        except Exception:
            logging.error(traceback.format_exc())

            min_value = 0
            max_value = 0
        self.context_dict['min_value'] = min_value
        self.context_dict['max_value'] = max_value

        self.context_dict['company_data'] = self.core_obj.get_all_company_source_objects(
            {'page': request.GET.get('page', 1), 'number-of-results-per-page': 10})
        self.context_dict['organisation_revenue_range'] = organisation_revenue_range
        self.context_dict['credits_remaining'] = PaymentHandler().return_users_remaining_credits({'user': request.user})
        self.context_dict['total_number_of_pages'] = self.core_obj.get_page_metrics_for_all_company_data()
        self.context_dict['total_count'] = CoreHandler().return_all_data_count()
        return render(request, 'client_company_list.html', self.context_dict)


@method_decorator(login_required, name='get')
class CompanySourceJSONView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request, *args, **kwargs):
        """
        This view enables chat functionality for the staff
        :param request:
        :return:
        """
        data = {
            'seniority_selected': request.GET.getlist('seniority_selected[]'),
            'country_select': request.GET.getlist('country_select[]'),
            'industry_select': request.GET.getlist('industry_select[]'),
            'page': request.GET.get('page', 1),
            'id_organization_revenue_in_thousands_int_min': request.GET.get(
                'id_organization_revenue_in_thousands_int_min'),
            'id_organization_revenue_in_thousands_int_max': request.GET.get(
                'id_organization_revenue_in_thousands_int_max'),
        }
        all_company_data, total_count = self.core_obj.filter_company_data_json(data)
        message_data = {
            'all_company_data': all_company_data,
            'total_count': total_count,
        }

        return JsonResponse(message_data, safe=False)


@method_decorator(login_required, name='get')
class GetEmailPhoneJSONView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request, *args, **kwargs):

        company_data_id = request.GET.get('company_data_id')
        view_data = self.payment_obj.update_user_credits_once_user_views_data(
            {'user': request.user, 'company_data_id': company_data_id})
        credits_remaining = PaymentHandler().return_users_remaining_credits({'user': request.user})
        if view_data:
            company_data = self.core_obj.get_email_phone_by_company_data_id({'company_data_id': company_data_id})
            company_data['credits_remaining'] = credits_remaining
            email = company_data.get('email')
            if request.user.profile.is_premium_user():
                company_data['is_premium_user'] = True
            else:
                company_data['is_premium_user'] = False
            if email and request.user.profile.is_premium_user():
                try:
                    verify_email_obj = VerifyEmail(email=email)
                    final_return = verify_email_obj.verify()
                    is_email_valid = final_return.get('deliverable')
                    company_data['is_email_valid'] = is_email_valid
                except Exception:
                    company_data['is_email_valid'] = False
            else:

                company_data['is_email_valid'] = False
        else:
            company_data = {'email': 'No credits', 'phone': 'No credits', 'credits_remaining': credits_remaining,
                            'is_email_valid': False}
        return JsonResponse(company_data, safe=False)


@method_decorator(login_required, name='get')
class DownloadReportView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()

    def get(self, request):

        check_zero = request.GET.get('check_zero')
        if not check_zero == '1':
            remaining_credits = PaymentHandler().return_users_remaining_credits({'user': request.user})
            if remaining_credits <= 0:
                messages.error(request,
                               'You have not credits left. Please buy a new plan to be able to download company '
                               'information')
                return redirect('plans')
        report = CreateCSVReport()
        if request.GET.get('download_number'):
            try:
                download_number = int(request.GET.get('download_number'))
            except:
                download_number = 10
            filter_data = {
                'seniority_selected': request.GET.get('seniority_selected').split(','),
                'country_select': request.GET.get('country_select').split(','),
                'industry_select': request.GET.get('industry_select').split(','),
                'page': request.GET.get('page', 1),
                'id_organization_revenue_in_thousands_int_min': request.GET.get(
                    'id_organization_revenue_in_thousands_int_min'),
                'id_organization_revenue_in_thousands_int_max': request.GET.get(
                    'id_organization_revenue_in_thousands_int_max'),
                'user': request.user,
                'download_number': download_number,
            }
            file_location = report.add_company_details_bulk_download(filter_data)
        else:

            company_id_value_list_str = request.GET.get('company_id_value_list')
            company_data_id_list = company_id_value_list_str.split(',')
            while "" in company_data_id_list:
                company_data_id_list.remove("")
            file_location = report.add_company_details_by_id_list(company_data_id_list, request.user)
        file_name = ntpath.basename(file_location)
        file_location = file_location.replace('%20', ' ')
        with open(file_location, 'rb') as fh:
            mime_type, _ = mimetypes.guess_type(file_location)
            response = HttpResponse(fh.read(), content_type=mime_type)
            response['Content-Disposition'] = 'attachment;filename=%s' % file_name
            return response


@method_decorator(login_required, name='post')
class FieldsMappingJSONView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def post(self, request, *args, **kwargs):
        import pdb
        pdb.set_trace()

        return JsonResponse(data={}, safe=False)


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class FieldsMappingView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request):
        if not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')
            return redirect('client_home')
        self.context_dict['company_source_field_input_mapping_form'] = CompanySourceFieldInputsMappingForm()

        return render(request, 'fields.html', self.context_dict)

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')
            return redirect('client_home')
        form = CompanySourceFieldInputsMappingForm(request.POST)
        try:
            form.is_valid()
        except:
            pass
        data = form.cleaned_data
        upload_details = self.core_obj.create_fields_mapping({'user': request.user, 'fields_mapping': data})

        messages.success(request, 'Please pick the  JSON File containing the data.')
        return redirect(reverse('chunked_upload') + '?upload_details_id=' + str(upload_details.id))


@method_decorator(login_required, name='get')
class UploadStatusView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request):
        if not request.user.is_staff:
            messages.error(request, 'You are not allowed to access this page')
            return redirect('client_home')
        self.context_dict['processing_upload_exists'] = self.core_obj.update_upload_status()
        self.context_dict['all_file_uploads'] = self.core_obj.get_all_file_uploads()
        return render(request, 'upload_status.html', self.context_dict)


@method_decorator(login_required, name='get')
class CheckUploadStatusJSONView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_dict = {}
        self.core_obj = CoreHandler()
        self.payment_obj = PaymentHandler()

    def get(self, request):
        processing_upload_exists = self.core_obj.update_upload_status()
        data_list = self.core_obj.check_upload_status()
        return JsonResponse({'data_list': data_list, 'processing_upload_exists': processing_upload_exists}, safe=False)
