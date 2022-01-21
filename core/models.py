import datetime
import logging
import random
import string
import traceback

import pytz
from celery.result import AsyncResult
from chunked_upload.models import ChunkedUpload
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.files import File as DjangoFile
from django.core.paginator import Paginator
from django.db import models

from company_details.settings import TIME_ZONE
# Create your models here.
from config_master import file_status_choices, STATUS_UPLOADED, STATUS_PROCESSING, STATUS_COMPLETED

log = logging.getLogger(__name__)
tz = pytz.timezone(TIME_ZONE)
MyChunkedUpload = ChunkedUpload

data = {'first_name': 'Jim', 'last_name': 'Tavernelli', 'title': 'President & Chief Operating Officer',
        'seniori ty_level': "Owner", "department": 'Operations', 'company': 'KLH Engineers',
        'email': 'jtavernelliklhengrs.com', 'work_direct_phone': None, "employees": '51-200',
        'industrytype': 'Manufacturing', 'subindustry': 'mechanical or industrial engineering',
        'keywords': 'mechanical, electrical engineering, ince ntive & rebate management, plumbing engineering, fire protection, technology systems, commissioning, lighting design, energy solutions, leed design & su pport',
        'person_linkedin_url': 'http://www.linkedin.com/in/jim-tavernelli-sib3934',
        'website': 'http://www.kLhengrs.com', 'company_linkedin_url': 'http: //www.linkedin.com/company/kLh-engineers',
        'facebook_urt': 'https://www.facebook.com/kthengrs', 'twitter_urt': 'https://twitter.com/KLH_Engineers',
        'city': 'Fort Thomas', 'state': 'Kentucky', 'country': 'United States',
        'company_address': '1538 Alexandria Pike, Fort Thomas, Kentucky, United States, 4107 5-2530',
        'company_city': 'Fort Thomas', 'company_state': 'Kentucky', 'company country': 'Inited States',
        'companyphone': 8594428050.0, 'seo_description': 'KLH Engineers',
        'technologies': "Sendgrid, Constant Contact, Outlook, Hobile Friendly, Google Font API, WordPress.org, YouTube, Apache, Newton Softwa re, Google Analytics, reCAPTCHA, Google Tag Manager",
        'annual_revanue': '$1N-$10M'}


class CompanyDetails(models.Model):
    _id = models.CharField(unique=True, max_length=1000, default='')
    _index = models.CharField(max_length=1000, default='', null=True)
    _type = models.CharField(max_length=1000, default='', null=True)
    _score = models.CharField(max_length=1000, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class UploadDetails(models.Model):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    fields_mapping = models.JSONField(default=dict)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)


class CompanySource(models.Model):
    company_detail = models.OneToOneField(CompanyDetails, null=False, blank=False, on_delete=models.CASCADE,
                                          related_name='company_source')
    person_name = models.CharField(max_length=1000, default='', null=True)
    person_first_name_unanalyzed = models.CharField(max_length=1000, default='', null=True)
    person_last_name_unanalyzed = models.CharField(max_length=1000, default='', null=True)
    person_name_unanalyzed_downcase = models.CharField(max_length=1000, default='', null=True)
    person_title = models.CharField(max_length=1000, default='', null=True)
    person_functions = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000, default=list,
                                  null=True)
    person_seniority = models.CharField(max_length=1000, default='', null=True)
    person_email_status_cd = models.CharField(max_length=1000, default='', null=True)
    person_extrapolated_email_confidence = models.CharField(max_length=1000, default='', null=True)
    person_email = models.CharField(max_length=1000, default='', null=True)
    person_phone = models.CharField(max_length=1000, default='', null=True)
    person_sanitized_phone = models.CharField(max_length=1000, default='', null=True)
    person_email_analyzed = models.CharField(max_length=1000, default='', null=True)
    person_linkedin_url = models.URLField(max_length=1000, default='', null=True)
    person_detailed_function = models.CharField(max_length=1000, default='', null=True)
    person_title_normalized = models.CharField(max_length=1000, default='', null=True)
    primary_title_normalized_for_faceting = models.CharField(max_length=1000, default='', null=True)
    organization_id = models.CharField(max_length=1000, default='', null=True)
    organization_name = models.CharField(max_length=1000, default='', null=True)
    organization_revenue_in_thousands_int = models.IntegerField(default=0, null=True)
    sanitized_organization_name_unanalyzed = models.CharField(max_length=1000, default='', null=True)
    organization_retail_location_count = models.CharField(max_length=1000, default='', null=True)
    organization_public_symbol = models.CharField(max_length=1000, default='', null=True)
    organization_linkedin_company_size_tag_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                            size=1000, default=list, null=True)
    company_address = models.TextField(default='', null=True)
    organization_founded_year = models.CharField(max_length=1000, default='', null=True)
    organization_alexa_ranking = models.CharField(max_length=1000, default='', null=True)
    organization_num_current_employees = models.CharField(max_length=1000, default='', null=True)
    organization_relevant_keywords = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000,
                                                default=list, null=True)
    organization_relevant_keywords_str = models.TextField(default='', null=True)
    organization_industries = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000,
                                         default=list, null=True)
    organization_linkedin_specialties = models.TextField(default='', null=True)
    organization_angellist_markets = models.TextField(default='', null=True)
    organization_yelp_categories = models.TextField(default='', null=True)
    organization_keywords = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000, default=list,
                                       null=True)
    organization_linkedin_industry_tag_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                        size=1000, default=list, null=True)
    organization_linkedin_specialty_tag_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                         size=1000, default=list, null=True)
    organization_angellist_market_tag_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                       size=1000, default=list, null=True)
    organization_short_description = models.TextField(default='', null=True)
    organization_seo_description = models.TextField(default='', null=True)
    organization_website_url = models.URLField(default='', null=True)
    organization_angellist_url = models.URLField(default='', null=True)
    organization_facebook_url = models.URLField(default='', null=True)
    organization_twitter_url = models.URLField(default='', null=True)
    organization_languages = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000,
                                        default=list, null=True)
    organization_num_languages = models.IntegerField(default=0, null=True)
    organization_linkedin_numerical_urls = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                      size=1000,
                                                      default=list, null=True)
    organization_domain_status_cd = models.IntegerField(default=0, null=True)
    organization_domain = models.CharField(max_length=1000, default='', null=True)
    organization_domain_analyzed = models.CharField(max_length=1000, default='', null=True)
    organization_phone = models.CharField(max_length=1000, default='', null=True)
    work_direct_phone = models.CharField(max_length=1000, default='', null=True)
    organization_all_possible_domains = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000,
                                                   default=list, null=True)
    organization_current_technologies = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=1000,
                                                   default=list, null=True)
    organization_num_linkedin_followers = models.IntegerField(default=0, null=True)
    job_functions = models.JSONField(default=dict, null=True)
    person_location_city = models.CharField(max_length=1000, default='', null=True)
    person_location_city_with_state_or_country = models.CharField(max_length=1000, default='', null=True)
    person_location_state = models.CharField(max_length=1000, default='', null=True)
    person_location_state_with_country = models.CharField(max_length=1000, default='', null=True)
    person_location_country = models.CharField(max_length=1000, default='', null=True)
    person_location_postal_code = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_city = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_city_with_state_or_country = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_state = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_state_with_country = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_country = models.CharField(max_length=1000, default='', null=True)
    organization_hq_location_postal_code = models.CharField(max_length=1000, default='', null=True)
    modality = models.CharField(max_length=1000, default='', null=True)
    organization_total_funding_long = models.CharField(max_length=1000, default='', null=True)
    organization_latest_funding_stage_cd = models.CharField(max_length=1000, default='', null=True)
    organization_latest_funding_round_amount_long = models.CharField(max_length=1000, default='', null=True)
    organization_latest_funding_round_date = models.CharField(max_length=1000, default='', null=True)
    string_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                            default=list, null=True)
    textarea_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                              default=list, null=True)
    number_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                            default=list, null=True)
    date_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                          default=list, null=True)
    datetime_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                              default=list, null=True)
    picklist_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                              default=list, null=True)
    boolean_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                             default=list, null=True)
    multipicklist_typed_custom_fields = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                                   default=list, null=True)
    label_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list, null=True)
    contact_label_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list,
                                   null=True)
    account_label_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list,
                                   null=True)
    account_stage_id = models.CharField(max_length=1000, default='', null=True)
    account_id = models.CharField(max_length=1000, default='', null=True)
    contact_emailer_campaign_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                              default=list, null=True)
    contact_prospect_import_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                             default=list, null=True)
    contact_email_verify_request_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                                  default=list, null=True)
    contact_lead_request_id = models.CharField(max_length=1000, default='', null=True)
    contact_source = models.CharField(max_length=1000, default='', null=True)
    salesforce_lead_id = models.CharField(max_length=1000, default='', null=True)
    salesforce_contact_id = models.CharField(max_length=1000, default='', null=True)
    account_owner_id = models.CharField(max_length=1000, default='', null=True)
    owner_id = models.CharField(max_length=1000, default='', null=True)
    contact_owner_id = models.CharField(max_length=1000, default='', null=True)
    prospected_by_team_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list,
                                        null=True)
    contact_unlocked = models.BooleanField(default=False, null=True)
    contact_email_replied = models.BooleanField(default=False, null=True)
    contact_email_clicked = models.BooleanField(default=False, null=True)
    contact_email_sent = models.BooleanField(default=False, null=True)
    contact_email_open = models.BooleanField(default=False, null=True)
    contact_email_unsubscribed = models.BooleanField(default=False, null=True)
    contact_email_spamblocked = models.BooleanField(default=False, null=True)
    contact_email_autoresponder = models.BooleanField(default=False, null=True)
    contact_demoed = models.BooleanField(default=False, null=True)
    contact_email_no_reply = models.BooleanField(default=False, null=True)
    contact_email_bounced = models.BooleanField(default=False, null=True)
    contact_stage_id = models.CharField(max_length=1000, default='', null=True)
    contact_created_at = models.CharField(max_length=1000, default='', null=True)
    contact_last_activity_date = models.CharField(max_length=1000, default='', null=True)
    contact_email_num_clicks = models.IntegerField(default=0, null=True)
    contact_email_num_opens = models.IntegerField(default=0, null=True)
    contact_engagement_score = models.IntegerField(default=0, null=True)
    contact_campaign_statuses = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                           default=list, null=True)
    contact_campaign_steps = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list,
                                        null=True)
    contact_campaign_statuses_or_failure_reasons = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                              size=10, default=list, null=True)
    contact_campaign_statuses_without_campaign_id = ArrayField(models.CharField(max_length=200, blank=True, null=True),
                                                               size=10, default=list, null=True)
    contact_campaign_send_from_aliases = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                                    default=list, null=True)
    contact_email_last_clicked_at = models.CharField(max_length=1000, default='', null=True)
    contact_email_last_opened_at = models.CharField(max_length=1000, default='', null=True)
    contact_phone_numbers = ArrayField(models.JSONField(null=True, blank=True, default=dict), size=1000, default=list,
                                       null=True)
    relavence_boost = models.IntegerField(default=0, null=True)
    contact_has_pending_email_arcgate_request = models.BooleanField(default=False, null=True)
    indexed_at = models.CharField(max_length=1000, default='', null=True)
    predictive_scores = models.CharField(max_length=1000, default='', null=True)
    test_predictive_score = models.CharField(max_length=1000, default='', null=True)
    account_zenflow_project_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10,
                                             default=list, null=True)
    zenflow_project_ids = ArrayField(models.CharField(max_length=200, blank=True, null=True), size=10, default=list,
                                     null=True)
    job_start_date = models.CharField(max_length=1000, default='', null=True)


class File(models.Model):
    json_file = models.FileField(null=False, upload_to='json_upload_files')
    start_processing_time = models.DateTimeField(null=True, blank=True)
    stop_processing_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=file_status_choices, default=STATUS_UPLOADED, null=True,
                              blank=True)
    updated_number = models.IntegerField(default=0)
    created_number = models.IntegerField(default=0)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)


class CoreManager:
    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def add_json_file_to_file_object(self, data):
        file = File.objects.get(id=data.get('json_file_id'))
        local_file = open(data.get('json_file_path'), 'rb')
        djangofile = DjangoFile(local_file)
        file.json_file.save(f'{self.randomword(30)}.json', djangofile)
        return file

    def update_upload_status(self):
        """
        This function updates the status of file uploads
        :return:
        """
        all_processing_file_uploads = File.objects.filter(status=STATUS_PROCESSING)
        for file_upload in all_processing_file_uploads:
            res = AsyncResult(file_upload.task_id)
            if res.ready():
                try:
                    file_upload.created_number = res.get()[0]
                    file_upload.updated_number = res.get()[1]
                except:
                    pass
                file_upload.status = STATUS_COMPLETED
                file_upload.stop_processing_time = datetime.datetime.now(tz)
                file_upload.save()
            else:
                continue
        return File.objects.filter(status=STATUS_PROCESSING).exists()

    def check_upload_status(self):
        """
        This function check all upload items and checks their upload status
        :return:
        """
        all_file_uploads = File.objects.all().order_by('-id')
        all_file_upload_details = []
        for file_upload in all_file_uploads:
            try:
                all_file_upload_details.append(
                    {
                        'json_file': file_upload.json_file.name,
                        'start_processing_time': file_upload.start_processing_time,
                        'status': file_upload.status,
                        'created_number': file_upload.created_number,
                        'updated_number': file_upload.updated_number,
                        'created_on': file_upload.created_on.strftime("%b,%d,%Y,%H:%M:%S"),
                    }
                )

            except Exception:
                logging.error(traceback.format_exc())
                continue
        return all_file_upload_details

    def get_all_file_uploads(self):
        """
        This function returns file uploads that contain a task id
        :return:
        """
        return File.objects.all().order_by('-id')

    def add_task_id_to_file(self, data):
        """
        This function assign a task id from a celery task to a file object
        :param data: {'task_id': The Task ID value from a celery task, 'file_id': The ID value of the file}
        :return:
        """
        file = File.objects.get(id=data.get('file_id'))
        file.task_id = data.get('task_id')
        file.start_processing_time = datetime.datetime.now(tz=tz)
        file.status = STATUS_PROCESSING
        file.save()
        return file

    def create_fields_mapping(self, data):
        """
        This function creates company details
        :param data: {'user': The current user, 'fields_mapping': The field mapping data}
        :return:
        """
        return UploadDetails.objects.create(
            created_by=data.get('user'),
            fields_mapping=data.get('fields_mapping'),
        )

    def create_file(self, data):
        """
        This function creates a new instance of a file object
        :param data: {'json_file': The json_file object}
        :return:
        """
        return File.objects.create(json_file=data.get('json_file'))

    def get_file_by_id(self, data):
        return File.objects.get(id=data.get('json_file_id'))

    def get_all_company_source_objects(self, data):
        """
        This function returns all the company source objects filtered by page
        :param data: {'page': The page number of the result, 'number-of-results-per-page': The number of pages per page}
        :return End attendance objects
        """
        result = CompanySource.objects.all().order_by('-id')
        if data.get('number-of-results-per-page'):
            paginator = Paginator(result, 10)
        else:
            paginator = Paginator(result, 200)
        page = data.get('page')
        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result

        return selected_results

    def filter_company_source_objects(self, data):
        """
        This function returns all the company source objects that match filter parameters provided
        :param data: {'page': The page number of the result, 'search-option':The filter option,
         'search-value': Search Value}
        :return End attendance objects
        """
        if data.get('order_by') == 'asc':
            order_by = 'id'
        else:
            order_by = '-id'
        if data.get('search-option') == 'person_name':
            result = CompanySource.objects.filter(person_name__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'person_title':
            result = CompanySource.objects.filter(person_title__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'person_location_city':
            result = CompanySource.objects.filter(person_location_city__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_state':
            result = CompanySource.objects.filter(person_location_state__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_country':
            result = CompanySource.objects.filter(person_location_country__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_name':
            result = CompanySource.objects.filter(organization_name__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_id':
            result = CompanySource.objects.filter(organization_id__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_founded_year':
            result = CompanySource.objects.filter(
                organization_founded_year__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_industry_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_industry_tag_ids__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_specialty_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_specialty_tag_ids__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'organization_languages':
            result = CompanySource.objects.filter(organization_languages__icontains=data.get('search-value')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_current_technologies':
            result = CompanySource.objects.filter(
                organization_current_technologies__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_city':
            result = CompanySource.objects.filter(
                organization_hq_location_city__icontains=data.get('search-value')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_state':
            result = CompanySource.objects.filter(
                organization_hq_location_state__icontains=data.get('search-value')).order_by(order_by)
        else:
            result = CompanySource.objects.all().order_by(order_by)

        paginator = Paginator(result, int(data.get('number-of-results-per-page')))
        page = data.get('page')
        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result

        return selected_results

    def filter_company_source_objects_according_to_siniority(self, data):
        """
        This function returns all the company source objects that match filter parameters provided
        :param data: {'page': The page number of the result, 'search-value': Search Value,
        'order_by': The order by value, 'number-of-results-per-page': The number of results per page}
        :return End attendance objects
        """
        if data.get('order_by') == 'asc':
            order_by = 'id'
        else:
            order_by = '-id'
        if data.get('search-option') == 'person_name':
            result = CompanySource.objects.filter(person_name__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'person_title':
            result = CompanySource.objects.filter(person_title__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'person_location_city':
            result = CompanySource.objects.filter(person_location_city__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_state':
            result = CompanySource.objects.filter(person_location_state__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_country':
            result = CompanySource.objects.filter(person_location_country__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_name':
            result = CompanySource.objects.filter(organization_name__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_id':
            result = CompanySource.objects.filter(organization_id__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_founded_year':
            result = CompanySource.objects.filter(
                organization_founded_year__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_industry_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_industry_tag_ids__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_specialty_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_specialty_tag_ids__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'organization_languages':
            result = CompanySource.objects.filter(organization_languages__icontains=data.get('search-value'),
                                                  person_seniority__icontains=data.get(
                                                      'search-option-seniority')).order_by(
                order_by)
        elif data.get('search-option') == 'organization_current_technologies':
            result = CompanySource.objects.filter(
                organization_current_technologies__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_city':
            result = CompanySource.objects.filter(
                organization_hq_location_city__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_state':
            result = CompanySource.objects.filter(
                organization_hq_location_state__icontains=data.get('search-value'),
                person_seniority__icontains=data.get('search-option-seniority')).order_by(order_by)
        else:
            result = CompanySource.objects.all().order_by(order_by)

        paginator = Paginator(result, int(data.get('number-of-results-per-page')))
        page = data.get('page')
        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result

        return selected_results

    def filter_company_source_objects_according_to_country(self, data):
        """
        This function returns all the company source objects that match filter parameters provided
        :param data: {'page': The page number of the result, 'search-value': Search Value,
        'order_by': The order by value, 'number-of-results-per-page': The number of results per page}
        :return End attendance objects
        """
        if data.get('order_by') == 'asc':
            order_by = 'id'
        else:
            order_by = '-id'
        if data.get('search-option') == 'person_name':
            result = CompanySource.objects.filter(person_name__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'person_title':
            result = CompanySource.objects.filter(person_title__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'person_location_city':
            result = CompanySource.objects.filter(person_location_city__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'person_location_state':
            result = CompanySource.objects.filter(person_location_state__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_name':
            result = CompanySource.objects.filter(organization_name__icontains=data.get('search-value'),
                                                  pperson_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_id':
            result = CompanySource.objects.filter(organization_id__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_founded_year':
            result = CompanySource.objects.filter(
                organization_founded_year__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_industry_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_industry_tag_ids__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_specialty_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_specialty_tag_ids__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_languages':
            result = CompanySource.objects.filter(organization_languages__icontains=data.get('search-value'),
                                                  person_location_country__icontains=data.get(
                                                      'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_current_technologies':
            result = CompanySource.objects.filter(
                organization_current_technologies__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_city':
            result = CompanySource.objects.filter(
                organization_hq_location_city__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_state':
            result = CompanySource.objects.filter(
                organization_hq_location_state__icontains=data.get('search-value'),
                person_location_country__icontains=data.get(
                    'person_location_country')).order_by(order_by)
        else:
            result = CompanySource.objects.all().order_by(order_by)

        paginator = Paginator(result, int(data.get('number-of-results-per-page')))
        page = data.get('page')
        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result

        return selected_results

    def filter_company_source_objects_according_to_revenue_range(self, data):
        """
        This function returns all the company source objects that match filter parameters provided
        :param data: {'page': The page number of the result, 'search-value': Search Value,
        'order_by': The order by value, 'number-of-results-per-page': The number of results per page}
        :return End attendance objects
        """
        if data.get('order_by') == 'asc':
            order_by = 'id'
        else:
            order_by = '-id'
        if data.get('search-option') == 'person_name':
            result = CompanySource.objects.filter(person_name__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'person_title':
            result = CompanySource.objects.filter(person_title__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_city':
            result = CompanySource.objects.filter(person_location_city__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'person_location_state':
            result = CompanySource.objects.filter(person_location_state__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'organization_name':
            result = CompanySource.objects.filter(organization_name__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'organization_id':
            result = CompanySource.objects.filter(organization_id__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'organization_founded_year':
            result = CompanySource.objects.filter(
                organization_founded_year__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_industry_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_industry_tag_ids__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        elif data.get('search-option') == 'organization_linkedin_specialty_tag_ids':
            result = CompanySource.objects.filter(
                organization_linkedin_specialty_tag_ids__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        elif data.get('search-option') == 'organization_languages':
            result = CompanySource.objects.filter(organization_languages__icontains=data.get('search-value'),
                                                  organization_revenue_in_thousands_int__range=[data.get(
                                                      'search-value-min'), data.get('search-value-max')]).order_by(
                order_by)
        elif data.get('search-option') == 'organization_current_technologies':
            result = CompanySource.objects.filter(
                organization_current_technologies__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_city':
            result = CompanySource.objects.filter(
                organization_hq_location_city__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        elif data.get('search-option') == 'organization_hq_location_state':
            result = CompanySource.objects.filter(
                organization_hq_location_state__icontains=data.get('search-value'),
                organization_revenue_in_thousands_int__range=[data.get(
                    'search-value-min'), data.get('search-value-max')]).order_by(order_by)
        else:
            result = CompanySource.objects.all().order_by(order_by)

        paginator = Paginator(result, int(data.get('number-of-results-per-page')))
        page = data.get('page')
        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result

        return selected_results

    def get_company_source_by_source_id(self, data):
        """
        This function returns a particular company source object by source id
        :param data: {'company_source_id': The ID value of the company source}
        :return:
        """
        return CompanySource.objects.get(id=data.get('company_source_id'))

    def return_all_data_count(self):
        """
        This function returns the count of all the data that is currently saved
        :return:
        """
        return CompanySource.objects.all().count()

    def get_email_phone_by_company_data_id(self, data):
        """
        This function returns
        :param data: {'company_data_id': The ID value of the company source data}
        :return:
        """
        company_data = CompanySource.objects.get(id=data.get('company_data_id'))
        return {'email': company_data.person_email, 'phone': company_data.person_phone}

    def listToString(self, s):

        # initialize an empty string
        str1 = " "
        if s == None:
            s = ''

        # return string
        return (str1.join(s))

    def convert_company_source_data_into_json(self, selected_results):
        """
        This function converts a queryset of company source into a json for ajax requests
        :param selected_results:
        :return:
        """
        all_company_data = []
        try:

            for company_data in selected_results.object_list:

                first_name = company_data.person_first_name_unanalyzed
                last_name = company_data.person_last_name_unanalyzed
                person_title = company_data.person_title
                person_seniority = company_data.person_seniority
                person_linkedin_url = company_data.person_linkedin_url
                organization_facebook_url = company_data.organization_facebook_url
                organization_twitter_url = company_data.organization_twitter_url
                organization_linkedin_numerical_urls = self.listToString(
                    company_data.organization_linkedin_numerical_urls)
                organization_relevant_keywords = self.listToString(company_data.organization_relevant_keywords)
                organization_industries = self.listToString(company_data.organization_industries)
                organization_name = company_data.organization_name
                organization_website_url = company_data.organization_website_url
                if company_data.organization_linkedin_numerical_urls:
                    try:
                        organization_linkedin_url = company_data.organization_linkedin_numerical_urls[0]
                    except:
                        organization_linkedin_url = '#'
                else:
                    organization_linkedin_url = '#'
                if organization_website_url is None:
                    organization_website_url = '#'
                if first_name is None:
                    first_name = ''
                if last_name is None:
                    last_name = ''
                if person_title is None:
                    person_title = ''
                if person_seniority is None:
                    person_seniority = ''
                if person_linkedin_url is None:
                    person_linkedin_url = '#'
                if organization_facebook_url is None:
                    organization_facebook_url = '#'
                if organization_twitter_url is None:
                    organization_twitter_url = '#'
                if organization_name == None:
                    organization_name = ''

                all_company_data.append({
                    'id': company_data.id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'organization_name': organization_name,
                    'organization_website_url': organization_website_url,
                    'person_title': person_title,
                    'person_seniority': person_seniority,
                    'person_linkedin_url': person_linkedin_url,
                    'organization_facebook_url': organization_facebook_url,
                    'organization_twitter_url': organization_twitter_url,
                    'organization_linkedin_numerical_urls': organization_linkedin_numerical_urls,
                    'organization_relevant_keywords': organization_relevant_keywords,
                    'organization_industries': organization_industries,
                    'organization_linkedin_url': organization_linkedin_url,
                })
        except Exception:
            logging.error(traceback.format_exc())
        return all_company_data

    def convert_company_source_data_into_json_queryset(self, selected_results):
        """
        This function converts a queryset of company source into a json for ajax requests
        :param selected_results:
        :return:
        """
        all_company_data = []
        try:
            for company_data in selected_results:
                first_name = company_data.person_first_name_unanalyzed
                last_name = company_data.person_last_name_unanalyzed
                person_title = company_data.person_title
                person_seniority = company_data.person_seniority
                person_linkedin_url = company_data.person_linkedin_url
                organization_facebook_url = company_data.organization_facebook_url
                organization_twitter_url = company_data.organization_twitter_url
                try:
                    organization_linkedin_numerical_urls = self.listToString(
                        company_data.organization_linkedin_numerical_urls)
                except:
                    organization_linkedin_numerical_urls = None
                try:
                    organization_relevant_keywords = self.listToString(company_data.organization_relevant_keywords)
                except:
                    organization_relevant_keywords = None
                try:
                    organization_industries = self.listToString(company_data.organization_industries)
                except:
                    organization_industries = None
                if not first_name:
                    first_name = ''
                if not last_name:
                    last_name = ''
                if not person_title:
                    person_title = ''
                if not person_seniority:
                    person_seniority = ''
                if not person_linkedin_url:
                    person_linkedin_url = '#'
                if not organization_facebook_url:
                    organization_facebook_url = '#'
                if not organization_twitter_url:
                    organization_twitter_url = '#'
                if company_data.organization_linkedin_numerical_urls:
                    try:
                        organization_linkedin_url = company_data.organization_linkedin_numerical_urls[0]
                    except:
                        organization_linkedin_url = '#'
                else:
                    organization_linkedin_url = '#'

                all_company_data.append({
                    'id': company_data.id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'person_title': person_title,
                    'person_seniority': person_seniority,
                    'person_linkedin_url': person_linkedin_url,
                    'organization_facebook_url': organization_facebook_url,
                    'organization_twitter_url': organization_twitter_url,
                    'organization_linkedin_numerical_urls': organization_linkedin_numerical_urls,
                    'organization_relevant_keywords': organization_relevant_keywords,
                    'organization_industries': organization_industries,
                    'organization_linkedin_url': organization_linkedin_url,
                })
        except Exception:
            logging.error(traceback.format_exc())
        return all_company_data

    def main_company_data_filter(self, data):
        """
        This function filters company data objects and returns a queryset
        :param data:
        :return:
        """
        filters = {}
        if data.get('seniority_selected'):
            filters['person_seniority__in'] = data.get('seniority_selected')
        if data.get('country_select'):
            filters['organization_hq_location_country__in'] = data.get('country_select')
        if data.get('industry_select'):
            filters['organization_industries'] = data.get('industry_select')
        if data.get('id_organization_revenue_in_thousands_int_min') and data.get(
                'id_organization_revenue_in_thousands_int_max'):
            filters['organization_revenue_in_thousands_int__range'] = (data.get(
                'id_organization_revenue_in_thousands_int_min'), data.get(
                'id_organization_revenue_in_thousands_int_max'))

        return CompanySource.objects.filter(**filters).order_by('-id')

    def filter_company_data_json(self, data):

        """
        This function filters Company Source data for ajax filter requests
        :param data: {'seniority_selected':List of seniority values, 'country_select': List of country values,
         'industry_select': List of industry values}
        :return:
        """
        result = self.main_company_data_filter(data)
        total_count = len(result)
        paginator = Paginator(result, 10)
        page = data.get('page')

        try:
            selected_results = paginator.page(page)
        except Exception:
            logging.error(traceback.format_exc())
            return []

        return self.convert_company_source_data_into_json(selected_results), total_count

    def get_page_metrics_for_all_company_data(self):
        """
        This function returns all the information about page number and totals of the company source data saved
        :return:
        """
        return CompanySource.objects.all().count() / 10

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def clean_array_input(self, returned_value):
        if returned_value and isinstance(returned_value, list):
            return returned_value
        else:
            if not returned_value:
                return None
            else:
                return [returned_value]

    def clean_int_input(self, returned_value):
        if returned_value and isinstance(returned_value, int):
            return returned_value
        elif returned_value and isinstance(returned_value, str):
            try:
                return int(returned_value)
            except ValueError:
                return 0
        else:
            if not returned_value:
                return 0
            else:
                return 0

    def old_update_function(self, company_data, upload_details_id):
        create = 0
        update = 0
        upload_details = UploadDetails.objects.filter(id=upload_details_id).last()

        company_details_obj = CompanyDetails.objects.filter(_id=company_data.get('_id'))
        if not company_details_obj:
            company_details_obj = CompanyDetails.objects.create(_id=self.randomword(20))

        if CompanySource.objects.filter(company_detail=company_details_obj).exists():
            company_source = CompanySource.objects.filter(company_detail=company_details_obj).last()
            update = 1
        elif CompanySource.objects.filter(person_email=company_data.get(
                upload_details.fields_mapping.get('person_email', 'email'))).exists():
            company_source = CompanySource.objects.filter(person_email=company_data.get(
                upload_details.fields_mapping.get('person_email', 'email'))).last()
            update = 1
        else:
            company_source = CompanySource.objects.create(company_detail=company_details_obj)
            create = 1
        try:
            company_source.person_name = company_data.get('person_name')
            company_source.person_first_name_unanalyzed = company_data.get('person_first_name_unanalyzed')
            company_source.person_last_name_unanalyzed = company_data.get('person_last_name_unanalyzed')
            company_source.person_name_unanalyzed_downcase = company_data.get(
                'person_name_unanalyzed_downcase')
            company_source.person_title = company_data.get('person_title')
            company_source.person_functions = self.clean_array_input(company_data.get('person_functions'))
            company_source.person_seniority = company_data.get('person_seniority')
            company_source.person_email_status_cd = company_data.get('person_email_status_cd')
            company_source.person_extrapolated_email_confidence = company_data.get(
                'person_extrapolated_email_confidence')
            company_source.person_email = company_data.get('person_email')
            company_source.person_phone = company_data.get('person_phone')
            company_source.person_sanitized_phone = company_data.get('person_sanitized_phone')
            company_source.person_email_analyzed = company_data.get('person_email_analyzed')
            company_source.person_linkedin_url = company_data.get('person_linkedin_url')
            company_source.person_detailed_function = company_data.get('person_detailed_function')
            company_source.person_title_normalized = company_data.get('person_title_normalized')
            company_source.primary_title_normalized_for_faceting = company_data.get(
                'primary_title_normalized_for_faceting')
            company_source.organization_id = company_data.get('organization_id')
            company_source.organization_name = company_data.get('organization_name')
            company_source.organization_revenue_in_thousands_int = self.clean_int_input(company_data.get(
                'organization_revenue_in_thousands_int'))
            company_source.sanitized_organization_name_unanalyzed = company_data.get(
                'sanitized_organization_name_unanalyzed')
            company_source.organization_retail_location_count = company_data.get(
                'organization_retail_location_count')
            company_source.organization_public_symbol = company_data.get('organization_public_symbol')
            company_source.organization_linkedin_company_size_tag_ids = self.clean_array_input(company_data.get(
                'organization_linkedin_company_size_tag_ids'))
            company_source.organization_founded_year = company_data.get('organization_founded_year')
            company_source.organization_alexa_ranking = company_data.get('organization_alexa_ranking')
            company_source.organization_num_current_employees = company_data.get(
                'organization_num_current_employees')
            company_source.organization_relevant_keywords = self.clean_array_input(company_data.get(
                'organization_relevant_keywords'))
            company_source.organization_relevant_keywords_str = company_data.get(
                'organization_relevant_keywords_str')
            company_source.organization_industries = self.clean_array_input(company_data.get('organization_industries'))
            company_source.organization_linkedin_specialties = company_data.get(
                'organization_linkedin_specialties')
            company_source.organization_angellist_markets = company_data.get(
                'organization_angellist_markets')
            company_source.organization_yelp_categories = company_data.get('organization_yelp_categories')
            company_source.organization_keywords = self.clean_array_input(company_data.get('organization_keywords'))
            company_source.organization_linkedin_industry_tag_ids = self.clean_array_input(company_data.get(
                'organization_linkedin_industry_tag_ids'))
            company_source.organization_linkedin_specialty_tag_ids = self.clean_array_input(company_data.get(
                'organization_linkedin_specialty_tag_ids'))
            company_source.organization_angellist_market_tag_ids = self.clean_array_input(company_data.get(
                'organization_angellist_market_tag_ids'))
            company_source.organization_short_description = company_data.get(
                'organization_short_description')
            company_source.organization_seo_description = company_data.get('organization_seo_description')
            company_source.organization_website_url = company_data.get('organization_website_url')
            company_source.organization_angellist_url = company_data.get('organization_angellist_url')
            company_source.organization_facebook_url = company_data.get('organization_facebook_url')
            company_source.organization_twitter_url = company_data.get('organization_twitter_url')
            company_source.organization_languages = self.clean_array_input(company_data.get('organization_languages'))
            company_source.organization_num_languages = company_data.get('organization_num_languages')
            company_source.organization_linkedin_numerical_urls = self.clean_array_input(company_data.get(
                'organization_linkedin_numerical_urls'))
            company_source.organization_domain_status_cd = company_data.get('organization_domain_status_cd')
            company_source.organization_domain = company_data.get('organization_domain')
            company_source.organization_domain_analyzed = company_data.get('organization_domain_analyzed')
            company_source.organization_phone = company_data.get('organization_phone')
            company_source.organization_all_possible_domains = self.clean_array_input(company_data.get(
                'organization_all_possible_domains'))
            company_source.organization_current_technologies = self.clean_array_input(company_data.get(
                'organization_current_technologies'))
            company_source.organization_num_linkedin_followers = company_data.get(
                'organization_num_linkedin_followers')
            company_source.job_functions = company_data.get('job_functions')
            company_source.person_location_city = company_data.get('person_location_city')
            company_source.person_location_city_with_state_or_country = company_data.get(
                'person_location_city_with_state_or_country')
            company_source.person_location_state = company_data.get('person_location_state')
            company_source.person_location_state_with_country = company_data.get(
                'person_location_state_with_country')
            company_source.person_location_country = company_data.get('person_location_country')
            company_source.person_location_postal_code = company_data.get('person_location_postal_code')
            company_source.organization_hq_location_city = company_data.get('organization_hq_location_city')
            company_source.organization_hq_location_city_with_state_or_country = company_data.get(
                'organization_hq_location_city_with_state_or_country')
            company_source.organization_hq_location_state = company_data.get(
                'organization_hq_location_state')
            company_source.organization_hq_location_state_with_country = company_data.get(
                'organization_hq_location_state_with_country')
            company_source.organization_hq_location_country = company_data.get(
                'organization_hq_location_country')
            company_source.organization_hq_location_postal_code = company_data.get(
                'organization_hq_location_postal_code')
            company_source.modality = company_data.get('modality')
            company_source.organization_total_funding_long = company_data.get(
                'organization_total_funding_long')
            company_source.organization_latest_funding_stage_cd = company_data.get(
                'organization_latest_funding_stage_cd')
            company_source.organization_latest_funding_round_amount_long = company_data.get(
                'organization_latest_funding_round_amount_long')
            company_source.organization_latest_funding_round_date = company_data.get(
                'organization_latest_funding_round_date')
            company_source.string_typed_custom_fields = self.clean_array_input(
                company_data.get('string_typed_custom_fields'))
            company_source.textarea_typed_custom_fields = self.clean_array_input(
                company_data.get('textarea_typed_custom_fields'))
            company_source.number_typed_custom_fields = self.clean_array_input(
                company_data.get('number_typed_custom_fields'))
            company_source.date_typed_custom_fields = self.clean_array_input(
                company_data.get('date_typed_custom_fields'))
            company_source.datetime_typed_custom_fields = self.clean_array_input(
                company_data.get('datetime_typed_custom_fields'))
            company_source.picklist_typed_custom_fields = self.clean_array_input(
                company_data.get('picklist_typed_custom_fields'))
            company_source.boolean_typed_custom_fields = self.clean_array_input(
                company_data.get('boolean_typed_custom_fields'))
            company_source.multipicklist_typed_custom_fields = self.clean_array_input(company_data.get(
                'multipicklist_typed_custom_fields'))
            company_source.label_ids = self.clean_array_input(company_data.get('label_ids'))
            company_source.contact_label_ids = self.clean_array_input(company_data.get('contact_label_ids'))
            company_source.account_label_ids = self.clean_array_input(company_data.get('account_label_ids'))
            company_source.account_stage_id = company_data.get('account_stage_id')
            company_source.account_id = company_data.get('account_id')
            company_source.contact_emailer_campaign_ids = self.clean_array_input(
                company_data.get('contact_emailer_campaign_ids'))
            company_source.contact_prospect_import_ids = self.clean_array_input(
                company_data.get('contact_prospect_import_ids'))
            company_source.contact_email_verify_request_ids = self.clean_array_input(company_data.get(
                'contact_email_verify_request_ids'))
            company_source.contact_lead_request_id = company_data.get('contact_lead_request_id')
            company_source.contact_source = company_data.get('contact_source')
            company_source.salesforce_lead_id = company_data.get('salesforce_lead_id')
            company_source.salesforce_contact_id = company_data.get('salesforce_contact_id')
            company_source.account_owner_id = company_data.get('account_owner_id')
            company_source.owner_id = company_data.get('owner_id')
            company_source.contact_owner_id = company_data.get('contact_owner_id')
            company_source.prospected_by_team_ids = self.clean_array_input(company_data.get('prospected_by_team_ids'))
            company_source.contact_unlocked = company_data.get('contact_unlocked')
            company_source.contact_email_replied = company_data.get('contact_email_replied')
            company_source.contact_email_clicked = company_data.get('contact_email_clicked')
            company_source.contact_email_sent = company_data.get('contact_email_sent')
            company_source.contact_email_open = company_data.get('contact_email_open')
            company_source.contact_email_unsubscribed = company_data.get('contact_email_unsubscribed')
            company_source.contact_email_spamblocked = company_data.get('contact_email_spamblocked')
            company_source.contact_email_autoresponder = company_data.get('contact_email_autoresponder')
            company_source.contact_demoed = company_data.get('contact_demoed')
            company_source.contact_email_no_reply = company_data.get('contact_email_no_reply')
            company_source.contact_email_bounced = company_data.get('contact_email_bounced')
            company_source.contact_stage_id = company_data.get('contact_stage_id')
            company_source.contact_created_at = company_data.get('contact_created_at')
            company_source.contact_last_activity_date = company_data.get('contact_last_activity_date')
            company_source.contact_email_num_clicks = company_data.get('contact_email_num_clicks')
            company_source.contact_email_num_opens = company_data.get('contact_email_num_opens')
            company_source.contact_engagement_score = company_data.get('contact_engagement_score')
            company_source.contact_campaign_statuses = self.clean_array_input(
                company_data.get('contact_campaign_statuses'))
            company_source.contact_campaign_steps = self.clean_array_input(company_data.get('contact_campaign_steps'))
            company_source.contact_campaign_statuses_or_failure_reasons = self.clean_array_input(company_data.get(
                'contact_campaign_statuses_or_failure_reasons'))
            company_source.contact_campaign_statuses_without_campaign_id = company_data.get(
                'contact_campaign_statuses_without_campaign_id')
            company_source.contact_campaign_send_from_aliases = company_data.get(
                'contact_campaign_send_from_aliases')
            company_source.contact_email_last_clicked_at = company_data.get('contact_email_last_clicked_at')
            company_source.contact_email_last_opened_at = company_data.get('contact_email_last_opened_at')
            company_source.contact_phone_numbers = self.clean_array_input(company_data.get('contact_phone_numbers'))
            company_source.relavence_boost = company_data.get('relavence_boost')
            company_source.contact_has_pending_email_arcgate_request = company_data.get(
                'contact_has_pending_email_arcgate_request')
            company_source.indexed_at = company_data.get('indexed_at')
            company_source.predictive_scores = company_data.get('predictive_scores')
            company_source.test_predictive_score = company_data.get('test_predictive_score')
            company_source.account_zenflow_project_ids = self.clean_array_input(
                company_data.get('account_zenflow_project_ids'))
            company_source.zenflow_project_ids = self.clean_array_input(company_data.get('zenflow_project_ids'))
            company_source.job_start_date = company_data.get('job_start_date')
            company_source.save()
            return [create, update]
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def new_update_function(self, company_data=data, upload_details_id=72, ):
        update = 0
        create = 0
        upload_details = UploadDetails.objects.filter(id=upload_details_id).last()
        if company_data.get('id'):
            company_details_obj = CompanyDetails.objects.filter(_id=company_data.get('id'))

            if not company_details_obj:
                company_details_obj = CompanyDetails.objects.create(_id=self.randomword(20))
        else:
            company_details_obj = CompanyDetails.objects.create(_id=self.randomword(20))

        if CompanySource.objects.filter(company_detail=company_details_obj).exists():
            company_source = CompanySource.objects.filter(company_detail=company_details_obj).last()
            update = 1
        elif CompanySource.objects.filter(person_email=company_data.get(
                upload_details.fields_mapping.get('person_email', 'email'))).exists():
            company_source = CompanySource.objects.filter(person_email=company_data.get(
                upload_details.fields_mapping.get('person_email', 'email'))).last()
            update = 1
        else:
            company_source = CompanySource.objects.create(company_detail=company_details_obj)
            create = 1
        try:
            company_source.person_name = company_data.get(
                upload_details.fields_mapping.get('person_name', 'person_name'))

            company_source.person_first_name_unanalyzed = company_data.get(upload_details.fields_mapping.get(
                'person_first_name_unanalyzed',
                'first_name'))

            company_source.person_last_name_unanalyzed = company_data.get(
                upload_details.fields_mapping.get('person_last_name_unanalyzed',
                                                  'last_name'))
            company_source.person_name_unanalyzed_downcase = company_data.get(
                upload_details.fields_mapping.get('person_name_unanalyzed_downcase',
                                                  'person_name_unanalyzed_downcase'))
            company_source.person_title = company_data.get(
                upload_details.fields_mapping.get('person_title', 'title'))
            company_source.person_functions = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('person_functions', 'person_functions')))
            company_source.person_seniority = company_data.get(
                upload_details.fields_mapping.get('person_seniority', 'person_seniority'))
            company_source.person_email_status_cd = company_data.get(
                upload_details.fields_mapping.get('person_email_status_cd', 'person_email_status_cd'))
            company_source.person_extrapolated_email_confidence = company_data.get(
                upload_details.fields_mapping.get('person_extrapolated_email_confidence',
                                                  'person_extrapolated_email_confidence'))
            company_source.person_email = company_data.get(
                upload_details.fields_mapping.get('person_email', 'email'))
            company_source.person_phone = company_data.get(
                upload_details.fields_mapping.get('person_phone', 'mobile_phone'))
            company_source.person_sanitized_phone = company_data.get(
                upload_details.fields_mapping.get('person_sanitized_phone', 'person_sanitized_phone'))
            company_source.person_email_analyzed = company_data.get(
                upload_details.fields_mapping.get('person_email_analyzed', 'person_email_analyzed'))
            company_source.person_linkedin_url = company_data.get(
                upload_details.fields_mapping.get('person_linkedin_url', 'linkedin_url'))
            company_source.person_detailed_function = company_data.get(
                upload_details.fields_mapping.get('person_detailed_function',
                                                  'person_detailed_function'))
            company_source.work_direct_phone = company_data.get(
                upload_details.fields_mapping.get('work_direct_phone',
                                                  'work_direct_phone'))
            company_source.person_title_normalized = company_data.get(
                upload_details.fields_mapping.get('person_title_normalized', 'person_title_normalized'))
            company_source.primary_title_normalized_for_faceting = company_data.get(
                upload_details.fields_mapping.get('primary_title_normalized_for_faceting',
                                                  'primary_title_normalized_for_faceting'))
            company_source.organization_id = company_data.get(
                upload_details.fields_mapping.get('organization_id', 'organization_id'))
            company_source.organization_name = company_data.get(
                upload_details.fields_mapping.get('organization_name', 'company'))
            company_source.organization_revenue_in_thousands_int = self.clean_int_input(company_data.get(
                upload_details.fields_mapping.get('organization_revenue_in_thousands_int',
                                                  'annual_revenue')))
            company_source.sanitized_organization_name_unanalyzed = company_data.get(
                upload_details.fields_mapping.get('sanitized_organization_name_unanalyzed',
                                                  'sanitized_organization_name_unanalyzed'))
            company_source.organization_retail_location_count = company_data.get(
                upload_details.fields_mapping.get('organization_retail_location_count',
                                                  'organization_retail_location_count'))
            company_source.organization_public_symbol = company_data.get(
                upload_details.fields_mapping.get('organization_public_symbol',
                                                  'organization_public_symbol'))
            company_source.organization_linkedin_company_size_tag_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_linkedin_company_size_tag_ids',
                                                  'organization_linkedin_company_size_tag_ids')))
            company_source.organization_founded_year = company_data.get(
                upload_details.fields_mapping.get('organization_founded_year',
                                                  'organization_founded_year'))
            company_source.organization_alexa_ranking = company_data.get(
                upload_details.fields_mapping.get('organization_alexa_ranking',
                                                  'organization_alexa_ranking'))
            company_source.organization_num_current_employees = company_data.get(
                upload_details.fields_mapping.get('organization_num_current_employees',
                                                  'employees'))
            company_source.organization_relevant_keywords = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_relevant_keywords',
                                                  'keywords')))
            company_source.organization_relevant_keywords_str = company_data.get(
                upload_details.fields_mapping.get('organization_relevant_keywords_str',
                                                  'keywords'))
            company_source.organization_industries = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_industries', 'industry')))
            company_source.organization_linkedin_specialties = company_data.get(
                upload_details.fields_mapping.get('organization_linkedin_specialties',
                                                  'organization_linkedin_specialties'))
            company_source.organization_angellist_markets = company_data.get(
                upload_details.fields_mapping.get('organization_angellist_markets',
                                                  'organization_angellist_markets'))
            company_source.organization_yelp_categories = company_data.get(
                upload_details.fields_mapping.get('organization_yelp_categories',
                                                  'organization_yelp_categories'))
            company_source.organization_keywords = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_keywords', 'organization_keywords')))
            company_source.organization_linkedin_specialty_tag_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_linkedin_specialty_tag_ids',
                                                  'organization_linkedin_specialty_tag_ids')))
            company_source.organization_angellist_market_tag_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_angellist_market_tag_ids',
                                                  'organization_angellist_market_tag_ids')))
            company_source.organization_short_description = company_data.get(
                upload_details.fields_mapping.get('organization_short_description',
                                                  'organization_short_description'))
            company_source.organization_seo_description = company_data.get(
                upload_details.fields_mapping.get('organization_seo_description',
                                                  'seo_description'))
            company_source.organization_website_url = company_data.get(
                upload_details.fields_mapping.get('organization_website_url',
                                                  'website'))
            company_source.organization_angellist_url = company_data.get(
                upload_details.fields_mapping.get('organization_angellist_url',
                                                  'organization_angellist_url'))
            company_source.organization_facebook_url = company_data.get(
                upload_details.fields_mapping.get('organization_facebook_url',
                                                  'facebook_url'))
            company_source.organization_twitter_url = company_data.get(
                upload_details.fields_mapping.get('organization_twitter_url',
                                                  'twitter_url'))
            company_source.organization_languages = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_languages', 'organization_languages')))
            company_source.organization_num_languages = company_data.get(
                upload_details.fields_mapping.get('organization_num_languages',
                                                  'organization_num_languages'))
            import pdb
            pdb.set_trace()
            company_source.organization_linkedin_numerical_urls = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_linkedin_numerical_urls',
                                                  'company_linkedin_url')))
            company_source.organization_domain_status_cd = company_data.get(
                upload_details.fields_mapping.get('organization_domain_status_cd',
                                                  'organization_domain_status_cd'))
            company_source.organization_domain = company_data.get(
                upload_details.fields_mapping.get('organization_domain', 'organization_domain'))
            company_source.organization_domain_analyzed = company_data.get(
                upload_details.fields_mapping.get('organization_domain_analyzed',
                                                  'organization_domain_analyzed'))
            company_source.organization_phone = company_data.get(
                upload_details.fields_mapping.get('organization_phone', 'company_phone'))
            company_source.organization_all_possible_domains = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_all_possible_domains',
                                                  'organization_all_possible_domains')))
            company_source.organization_current_technologies = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('organization_current_technologies',
                                                  'technologies')))
            company_source.organization_num_linkedin_followers = company_data.get(
                upload_details.fields_mapping.get('organization_num_linkedin_followers',
                                                  'organization_num_linkedin_followers'))
            company_source.job_functions = company_data.get(
                upload_details.fields_mapping.get('job_functions', 'job_functions'))
            company_source.person_location_city = company_data.get(
                upload_details.fields_mapping.get('person_location_city', 'city'))
            company_source.person_location_city_with_state_or_country = company_data.get(
                upload_details.fields_mapping.get('person_location_city_with_state_or_country',
                                                  'person_location_city_with_state_or_country'))
            company_source.person_location_state = company_data.get(
                upload_details.fields_mapping.get('person_location_state', 'state'))
            company_source.person_location_state_with_country = company_data.get(
                upload_details.fields_mapping.get('person_location_state_with_country',
                                                  'person_location_state_with_country'))
            company_source.person_location_country = company_data.get(
                upload_details.fields_mapping.get('person_location_country', 'country'))
            company_source.company_address = company_data.get(
                upload_details.fields_mapping.get('company_address', 'company_address'))
            company_source.person_location_postal_code = company_data.get(
                upload_details.fields_mapping.get('person_location_postal_code',
                                                  'person_location_postal_code'))
            company_source.organization_hq_location_city = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_city',
                                                  'company_city'))
            company_source.organization_hq_location_city_with_state_or_country = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_city_with_state_or_country',
                                                  'organization_hq_location_city_with_state_or_country'))
            company_source.organization_hq_location_state = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_state',
                                                  'company_state'))
            company_source.organization_hq_location_state_with_country = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_state_with_country',
                                                  'organization_hq_location_state_with_country'))
            company_source.organization_hq_location_country = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_country',
                                                  'company_country'))
            company_source.organization_hq_location_postal_code = company_data.get(
                upload_details.fields_mapping.get('organization_hq_location_postal_code',
                                                  'organization_hq_location_postal_code'))
            company_source.modality = company_data.get(
                upload_details.fields_mapping.get('modality', 'modality'))
            company_source.organization_total_funding_long = company_data.get(
                upload_details.fields_mapping.get('organization_total_funding_long',
                                                  'organization_total_funding_long'))
            company_source.organization_latest_funding_stage_cd = company_data.get(
                upload_details.fields_mapping.get('organization_latest_funding_stage_cd',
                                                  'organization_latest_funding_stage_cd'))
            company_source.organization_latest_funding_round_amount_long = company_data.get(
                upload_details.fields_mapping.get('organization_latest_funding_round_amount_long',
                                                  'organization_latest_funding_round_amount_long'))
            company_source.organization_latest_funding_round_date = company_data.get(
                upload_details.fields_mapping.get('organization_latest_funding_round_date',
                                                  'organization_latest_funding_round_date'))
            company_source.string_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('string_typed_custom_fields',
                                                  'string_typed_custom_fields')))
            company_source.textarea_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('textarea_typed_custom_fields',
                                                  'textarea_typed_custom_fields')))
            company_source.number_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('number_typed_custom_fields',
                                                  'number_typed_custom_fields')))
            company_source.date_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('date_typed_custom_fields',
                                                  'date_typed_custom_fields')))
            company_source.datetime_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('datetime_typed_custom_fields',
                                                  'datetime_typed_custom_fields')))
            company_source.picklist_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('picklist_typed_custom_fields',
                                                  'picklist_typed_custom_fields')))
            company_source.boolean_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('boolean_typed_custom_fields',
                                                  'boolean_typed_custom_fields')))
            company_source.multipicklist_typed_custom_fields = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('multipicklist_typed_custom_fields',
                                                  'multipicklist_typed_custom_fields')))
            company_source.label_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('label_ids', 'label_ids')))
            company_source.contact_label_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_label_ids', 'contact_label_ids')))
            company_source.account_label_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('account_label_ids', 'account_label_ids')))
            company_source.account_stage_id = company_data.get(
                upload_details.fields_mapping.get('account_stage_id', 'account_stage_id'))
            company_source.account_id = company_data.get(
                upload_details.fields_mapping.get('account_id', 'account_id'))
            company_source.contact_emailer_campaign_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_emailer_campaign_ids',
                                                  'contact_emailer_campaign_ids')))
            company_source.contact_prospect_import_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_prospect_import_ids',
                                                  'contact_prospect_import_ids')))
            company_source.contact_email_verify_request_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_email_verify_request_ids',
                                                  'contact_email_verify_request_ids')))
            company_source.contact_lead_request_id = company_data.get(
                upload_details.fields_mapping.get('contact_lead_request_id', 'contact_lead_request_id'))
            company_source.contact_source = company_data.get(
                upload_details.fields_mapping.get('contact_source', 'contact_source'))
            company_source.salesforce_lead_id = company_data.get(
                upload_details.fields_mapping.get('salesforce_lead_id', 'salesforce_lead_id'))
            company_source.salesforce_contact_id = company_data.get(
                upload_details.fields_mapping.get('salesforce_contact_id', 'salesforce_contact_id'))
            company_source.account_owner_id = company_data.get(
                upload_details.fields_mapping.get('account_owner_id', 'account_owner_id'))
            company_source.owner_id = company_data.get(
                upload_details.fields_mapping.get('owner_id', 'owner_id'))
            company_source.contact_owner_id = company_data.get(
                upload_details.fields_mapping.get('contact_owner_id', 'contact_owner_id'))
            company_source.prospected_by_team_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('prospected_by_team_ids', 'prospected_by_team_ids')))
            company_source.contact_unlocked = company_data.get(
                upload_details.fields_mapping.get('contact_unlocked', 'contact_unlocked'))
            company_source.contact_email_replied = company_data.get(
                upload_details.fields_mapping.get('contact_email_replied', 'contact_email_replied'))
            company_source.contact_email_clicked = company_data.get(
                upload_details.fields_mapping.get('contact_email_clicked', 'contact_email_clicked'))
            company_source.contact_email_sent = company_data.get(
                upload_details.fields_mapping.get('contact_email_sent', 'contact_email_sent'))
            company_source.contact_email_open = company_data.get(
                upload_details.fields_mapping.get('contact_email_open', 'contact_email_open'))
            company_source.contact_email_unsubscribed = company_data.get(
                upload_details.fields_mapping.get('contact_email_unsubscribed',
                                                  'contact_email_unsubscribed'))
            company_source.contact_email_spamblocked = company_data.get(
                upload_details.fields_mapping.get('contact_email_spamblocked',
                                                  'contact_email_spamblocked'))
            company_source.contact_email_autoresponder = company_data.get(
                upload_details.fields_mapping.get('contact_email_autoresponder',
                                                  'contact_email_autoresponder'))
            company_source.contact_demoed = company_data.get(
                upload_details.fields_mapping.get('contact_demoed', 'contact_demoed'))
            company_source.contact_email_no_reply = company_data.get(
                upload_details.fields_mapping.get('contact_email_no_reply', 'contact_email_no_reply'))
            company_source.contact_email_bounced = company_data.get(
                upload_details.fields_mapping.get('contact_email_bounced', 'contact_email_bounced'))
            company_source.contact_stage_id = company_data.get(
                upload_details.fields_mapping.get('contact_stage_id', 'contact_stage_id'))
            company_source.contact_created_at = company_data.get(
                upload_details.fields_mapping.get('contact_created_at', 'contact_created_at'))
            company_source.contact_last_activity_date = company_data.get(
                upload_details.fields_mapping.get('contact_last_activity_date',
                                                  'contact_last_activity_date'))
            company_source.contact_email_num_clicks = company_data.get(
                upload_details.fields_mapping.get('contact_email_num_clicks',
                                                  'contact_email_num_clicks'))
            company_source.contact_email_num_opens = company_data.get(
                upload_details.fields_mapping.get('contact_email_num_opens', 'contact_email_num_opens'))
            company_source.contact_engagement_score = company_data.get(
                upload_details.fields_mapping.get('contact_engagement_score',
                                                  'contact_engagement_score'))
            company_source.contact_campaign_statuses = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_campaign_statuses',
                                                  'contact_campaign_statuses')))
            company_source.contact_campaign_steps = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_campaign_steps', 'contact_campaign_steps')))
            company_source.contact_campaign_statuses_or_failure_reasons = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_campaign_statuses_or_failure_reasons',
                                                  'contact_campaign_statuses_or_failure_reasons')))
            company_source.contact_campaign_statuses_without_campaign_id = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_campaign_statuses_without_campaign_id',
                                                  'contact_campaign_statuses_without_campaign_id')))
            company_source.contact_campaign_send_from_aliases = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_campaign_send_from_aliases',
                                                  'contact_campaign_send_from_aliases')))
            company_source.contact_email_last_clicked_at = company_data.get(
                upload_details.fields_mapping.get('contact_email_last_clicked_at',
                                                  'contact_email_last_clicked_at'))
            company_source.contact_email_last_opened_at = company_data.get(
                upload_details.fields_mapping.get('contact_email_last_opened_at',
                                                  'contact_email_last_opened_at'))
            company_source.contact_phone_numbers = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('contact_phone_numbers', 'contact_phone_numbers')))
            company_source.relavence_boost = company_data.get(
                upload_details.fields_mapping.get('relavence_boost', 'relavence_boost'))
            company_source.contact_has_pending_email_arcgate_request = company_data.get(
                upload_details.fields_mapping.get('contact_has_pending_email_arcgate_request',
                                                  'contact_has_pending_email_arcgate_request'))
            company_source.indexed_at = company_data.get(
                upload_details.fields_mapping.get('indexed_at', 'indexed_at'))
            company_source.predictive_scores = company_data.get(
                upload_details.fields_mapping.get('predictive_scores', 'predictive_scores'))
            company_source.test_predictive_score = company_data.get(
                upload_details.fields_mapping.get('test_predictive_score', 'test_predictive_score'))
            company_source.account_zenflow_project_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('account_zenflow_project_ids',
                                                  'person_nameperson_name')))
            company_source.zenflow_project_ids = self.clean_array_input(company_data.get(
                upload_details.fields_mapping.get('zenflow_project_ids', 'zenflow_project_ids')))
            company_source.job_start_date = company_data.get(
                upload_details.fields_mapping.get('job_start_date', 'job_start_date'))
            company_source.save()
            return [create, update]

        except Exception:
            logging.error(traceback.format_exc())
            return None
