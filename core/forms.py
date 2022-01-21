from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.forms import ModelForm
from django_filters.fields import RangeField

from core.models import CompanySource


class CompanySourceFieldInputsMappingForm(ModelForm):
    person_functions = forms.CharField()
    organization_linkedin_company_size_tag_ids = forms.CharField()
    organization_relevant_keywords = forms.CharField()
    organization_industries = forms.CharField()
    organization_keywords = forms.CharField()
    organization_linkedin_industry_tag_ids = forms.CharField()
    organization_linkedin_specialty_tag_ids = forms.CharField()
    organization_angellist_market_tag_ids = forms.CharField()
    organization_languages = forms.CharField()
    organization_linkedin_numerical_urls = forms.CharField()
    organization_all_possible_domains = forms.CharField()
    organization_current_technologies = forms.CharField()
    string_typed_custom_fields = forms.CharField()
    textarea_typed_custom_fields = forms.CharField()
    number_typed_custom_fields = forms.CharField()
    date_typed_custom_fields = forms.CharField()
    datetime_typed_custom_fields = forms.CharField()
    picklist_typed_custom_fields = forms.CharField()
    boolean_typed_custom_fields = forms.CharField()
    multipicklist_typed_custom_fields = forms.CharField()
    label_ids = forms.CharField()
    contact_label_ids = forms.CharField()
    account_label_ids = forms.CharField()
    contact_emailer_campaign_ids = forms.CharField()
    contact_prospect_import_ids = forms.CharField()
    contact_email_verify_request_ids = forms.CharField()
    prospected_by_team_ids = forms.CharField()
    contact_campaign_statuses = forms.CharField()
    contact_campaign_steps = forms.CharField()
    contact_campaign_statuses_or_failure_reasons = forms.CharField()
    contact_campaign_statuses_without_campaign_id = forms.CharField()
    contact_campaign_send_from_aliases = forms.CharField()
    contact_phone_numbers = forms.CharField()
    account_zenflow_project_ids = forms.CharField()
    person_linkedin_url = forms.CharField()
    organization_website_url = forms.CharField()
    organization_angellist_url = forms.CharField()
    organization_facebook_url = forms.CharField()
    organization_twitter_url = forms.CharField()
    organization_revenue_in_thousands_int = forms.CharField()
    organization_num_languages = forms.CharField()
    organization_domain_status_cd = forms.CharField()
    organization_num_linkedin_followers = forms.CharField()
    contact_email_num_clicks = forms.CharField()
    contact_email_num_opens = forms.CharField()
    contact_engagement_score = forms.CharField()
    relavence_boost = forms.CharField()
    contact_unlocked = forms.CharField()
    contact_email_replied = forms.CharField()
    contact_email_clicked = forms.CharField()
    contact_email_sent = forms.CharField()
    contact_email_open = forms.CharField()
    contact_email_unsubscribed = forms.CharField()
    contact_email_spamblocked = forms.CharField()
    contact_email_autoresponder = forms.CharField()
    contact_demoed = forms.CharField()
    contact_email_no_reply = forms.CharField()
    contact_email_bounced = forms.CharField()
    organization_relevant_keywords_str = forms.CharField()
    organization_linkedin_specialties = forms.CharField()
    organization_angellist_markets = forms.CharField()
    organization_yelp_categories = forms.CharField()
    organization_short_description = forms.CharField()
    organization_seo_description = forms.CharField()
    job_functions = forms.CharField()
    contact_has_pending_email_arcgate_request = forms.CharField()
    zenflow_project_ids = forms.CharField()
    company_address = forms.CharField()
    work_direct_phone = forms.CharField()

    class Meta:
        model = CompanySource
        un_sorted_fields = ['person_name', 'person_first_name_unanalyzed', 'person_last_name_unanalyzed',
                            'person_name_unanalyzed_downcase', 'person_title', 'person_functions',
                            'person_seniority',
                            'person_email_status_cd', 'person_extrapolated_email_confidence', 'person_email',
                            'person_phone', 'person_sanitized_phone', 'person_email_analyzed',
                            'person_linkedin_url', 'person_detailed_function', 'person_title_normalized',
                            'primary_title_normalized_for_faceting', 'organization_id', 'organization_name',
                            'organization_revenue_in_thousands_int', 'sanitized_organization_name_unanalyzed',
                            'organization_retail_location_count',
                            'organization_public_symbol',
                            'organization_linkedin_company_size_tag_ids', 'organization_founded_year',
                            'organization_alexa_ranking',
                            'organization_num_current_employees', 'organization_relevant_keywords',
                            'organization_relevant_keywords_str',
                            'organization_industries', 'organization_linkedin_specialties',
                            'organization_angellist_markets',
                            'organization_yelp_categories',
                            'organization_keywords', 'organization_linkedin_industry_tag_ids',
                            'organization_linkedin_specialty_tag_ids',
                            'organization_angellist_market_tag_ids', 'organization_short_description',
                            'organization_seo_description', 'organization_website_url', 'organization_angellist_url',
                            'organization_facebook_url', 'organization_twitter_url', 'organization_languages',
                            'organization_num_languages', 'organization_linkedin_numerical_urls',
                            'organization_domain_status_cd',
                            'organization_domain', 'organization_domain_analyzed', 'organization_phone',
                            'organization_all_possible_domains', 'organization_current_technologies',
                            'organization_num_linkedin_followers',
                            'job_functions', 'person_location_city', 'person_location_city_with_state_or_country',
                            'person_location_state', 'person_location_state_with_country', 'person_location_country',
                            'person_location_postal_code', 'organization_hq_location_city',
                            'organization_hq_location_city_with_state_or_country',
                            'organization_hq_location_state', 'organization_hq_location_state_with_country',
                            'organization_hq_location_country',
                            'organization_hq_location_postal_code', 'modality', 'organization_total_funding_long',
                            'organization_latest_funding_stage_cd', 'organization_latest_funding_round_amount_long',
                            'organization_latest_funding_round_date',
                            'string_typed_custom_fields', 'textarea_typed_custom_fields', 'number_typed_custom_fields',
                            'date_typed_custom_fields', 'datetime_typed_custom_fields', 'picklist_typed_custom_fields',
                            'boolean_typed_custom_fields', 'multipicklist_typed_custom_fields', 'label_ids',
                            'contact_label_ids', 'account_label_ids', 'account_stage_id',
                            'account_id', 'contact_emailer_campaign_ids', 'contact_prospect_import_ids',
                            'contact_email_verify_request_ids', 'contact_lead_request_id', 'contact_source',
                            'salesforce_lead_id', 'salesforce_contact_id', 'account_owner_id',
                            'owner_id', 'contact_owner_id', 'prospected_by_team_ids',
                            'contact_unlocked', 'contact_email_replied', 'contact_email_clicked',
                            'contact_email_sent', 'contact_email_open', 'contact_email_unsubscribed',
                            'contact_email_spamblocked', 'contact_email_autoresponder', 'contact_demoed',
                            'contact_email_no_reply', 'contact_email_bounced', 'contact_stage_id', 'contact_created_at',
                            'contact_last_activity_date', 'contact_email_num_clicks', 'contact_email_num_opens',
                            'contact_stage_id',
                            'contact_created_at', 'contact_last_activity_date', 'contact_email_num_clicks',
                            'contact_email_num_opens',
                            'contact_engagement_score', 'contact_campaign_statuses', 'contact_campaign_steps',
                            'contact_campaign_statuses_or_failure_reasons',
                            'contact_campaign_statuses_without_campaign_id', 'contact_campaign_send_from_aliases',
                            'contact_email_last_clicked_at', 'contact_email_bounced',
                            'contact_email_last_opened_at', 'contact_phone_numbers', 'relavence_boost',
                            'contact_has_pending_email_arcgate_request',
                            'indexed_at', 'predictive_scores', 'test_predictive_score', 'account_zenflow_project_ids',
                            'zenflow_project_ids', 'job_start_date', 'company_address', 'work_direct_phone']
        un_sorted_fields.sort()
        fields = un_sorted_fields

    def __init__(self, *args, **kwargs):
        super(CompanySourceFieldInputsMappingForm, self).__init__(*args, **kwargs)
        exempted_fields = ['person_first_name_unanalyzed', 'person_last_name_unanalyzed', 'person_title', ]

        for visible in self.visible_fields():
            if visible.field != 'tour_start' or visible.field != 'tour_stop':
                visible.field.required = True
                visible.field.widget.attrs['value'] = visible.name
                visible.field.widget.attrs['class'] = 'form-control'
        self.fields['person_first_name_unanalyzed'].widget.attrs['value'] = 'first_name'
        self.fields['person_last_name_unanalyzed'].widget.attrs['value'] = 'last_name'
        self.fields['person_title'].widget.attrs['value'] = 'title'
        self.fields['person_email'].widget.attrs['value'] = 'email'
        self.fields['person_phone'].widget.attrs['value'] = 'mobile_phone'
        self.fields['person_linkedin_url'].widget.attrs['value'] = 'linkedin_url'
        self.fields['organization_name'].widget.attrs['value'] = 'company'
        self.fields['organization_revenue_in_thousands_int'].widget.attrs['value'] = 'annual_revenue'
        self.fields['organization_num_current_employees'].widget.attrs['value'] = 'employees'
        self.fields['organization_relevant_keywords'].widget.attrs['value'] = 'keywords'
        self.fields['organization_relevant_keywords_str'].widget.attrs['value'] = 'keywords'
        self.fields['organization_industries'].widget.attrs['value'] = 'industry'
        self.fields['organization_seo_description'].widget.attrs['value'] = 'seo_description'
        self.fields['organization_website_url'].widget.attrs['value'] = 'website'
        self.fields['organization_facebook_url'].widget.attrs['value'] = 'facebook_url'
        self.fields['organization_twitter_url'].widget.attrs['value'] = 'twitter_url'
        self.fields['organization_linkedin_numerical_urls'].widget.attrs['value'] = 'company_linkedin_url'
        self.fields['organization_phone'].widget.attrs['value'] = 'company_phone'
        self.fields['organization_current_technologies'].widget.attrs['value'] = 'technologies'
        self.fields['person_location_city'].widget.attrs['value'] = 'city'
        self.fields['person_location_state'].widget.attrs['value'] = 'state'
        self.fields['person_location_country'].widget.attrs['value'] = 'country'
        self.fields['organization_hq_location_city'].widget.attrs['value'] = 'company_city'
        self.fields['organization_hq_location_state'].widget.attrs['value'] = 'company_state'
        self.fields['organization_hq_location_country'].widget.attrs['value'] = 'company_country'


class PeopleFilterFormHelper(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'get'
        layout_fields = []
        for field_name, field in self.fields.items():
            if isinstance(field, RangeField):
                layout_field = Field(field_name, template="forms/fields/range-slider.html")
            else:
                layout_field = Field(field_name)
            layout_fields.append(layout_field)
        layout_fields.append(
            StrictButton("Search", name='search-submit', id='filter-submit', type='submit',
                         css_class='btn btn-primary btn-block mt-1'))
        self.helper.layout = Layout(*layout_fields)
