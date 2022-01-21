import csv
import json
import logging
import os
import random
import string
import traceback

import pandas as pd
from django.core.paginator import Paginator

from company_details.settings import BASE_DIR, MEDIA_ROOT
from core.core_handler import CoreHandler
from core.models import CompanySource
from payment.payment_handler import PaymentHandler

log = logging.getLogger(__name__)


class CreateCSVReport(object):
    def __init__(self):
        self.csv_document = os.path.join(BASE_DIR, 'documents_templates/test_document.csv')
        self.output_file = os.path.join(BASE_DIR, 'documents_templates/' + str(self.randomword(20)) + '.csv')

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def add_details(self, data):
        result = CoreHandler().main_company_data_filter(data)
        paginator = Paginator(result, 10)
        page = data.get('page', 1)

        try:
            selected_results = paginator.page(page)
        except Exception:
            selected_results = result
        with open(self.csv_document, 'r') as input_file, open(self.output_file, 'a', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                # do something with row
                writer.writerow(row)
            try:
                for item in selected_results.object_list:
                    view_data = PaymentHandler().update_user_credits_once_user_views_data(
                        {'user': data.get('user'), 'company_data_id': item.id})
                    if view_data:
                        writer.writerow(
                            [item.person_first_name_unanalyzed, item.person_last_name_unanalyzed, item.person_seniority,
                             item.person_title, item.person_email, item.person_email_status_cd, item.person_phone,
                             item.person_linkedin_url, item.person_detailed_function, item.organization_name,
                             item.organization_id, item.organization_revenue_in_thousands_int,
                             item.organization_website_url,
                             item.organization_phone, item.person_location_city_with_state_or_country])
                    else:
                        continue
            except Exception:
                logging.error(traceback.format_exc())
            input_file.close()
            output_file.close()
            return self.output_file

    def add_company_details_bulk_download(self, data):
        filters = {}
        if data.get('seniority_selected') and data.get('seniority_selected')[0] != '':
            filters['person_seniority__in'] = data.get('seniority_selected')
        if data.get('country_select') and data.get('country_select')[0] != '':
            filters['organization_hq_location_country__in'] = data.get('country_select')
        if data.get('industry_select') and data.get('industry_select')[0] != '':
            filters['organization_industries'] = data.get('industry_select')
        if data.get('id_organization_revenue_in_thousands_int_min') and data.get(
                'id_organization_revenue_in_thousands_int_max'):
            filters['organization_revenue_in_thousands_int__range'] = (data.get(
                'id_organization_revenue_in_thousands_int_min'), data.get(
                'id_organization_revenue_in_thousands_int_max'))

        results = CompanySource.objects.filter(**filters).order_by('-id')[:data.get('download_number')]
        user = data.get('user')
        with open(self.csv_document, 'r') as input_file, open(self.output_file, 'a', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                writer.writerow(row)
            try:
                for item in results:
                    view_data = PaymentHandler().update_user_credits_once_user_views_data(
                        {'user': user, 'company_data_id': item.id})
                    if view_data:
                        writer.writerow(
                            [item.person_first_name_unanalyzed, item.person_last_name_unanalyzed, item.person_title,
                             item.person_seniority,
                             item.person_email, item.person_email_status_cd, item.person_phone,
                             item.person_linkedin_url, item.person_detailed_function, item.organization_name,
                             item.organization_id, item.organization_revenue_in_thousands_int,
                             item.organization_website_url,
                             item.organization_phone, item.person_location_city_with_state_or_country])
                    else:
                        continue
            except Exception:
                logging.error(traceback.format_exc())
            input_file.close()
            output_file.close()
            return self.output_file

    def add_company_details_by_id_list(self, company_data_id_list, user):
        """
        This function adds company details in an excel file according to the the company data ID list
        :param user: The current logged in user
        :param company_data_id_list: [List containing the ID value of company Source]
        :return: excel download file
        """
        results = CompanySource.objects.filter(id__in=company_data_id_list)
        with open(self.csv_document, 'r') as input_file, open(self.output_file, 'a', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            for row in reader:
                writer.writerow(row)
            try:
                for item in results:
                    view_data = PaymentHandler().update_user_credits_once_user_views_data(
                        {'user': user, 'company_data_id': item.id})
                    if view_data:
                        writer.writerow(
                            [item.person_first_name_unanalyzed, item.person_last_name_unanalyzed, item.person_title,
                             item.person_seniority,
                             item.person_email, item.person_email_status_cd, item.person_phone,
                             item.person_linkedin_url, item.person_detailed_function, item.organization_name,
                             item.organization_id, item.organization_revenue_in_thousands_int,
                             item.organization_website_url,
                             item.organization_phone, item.person_location_city_with_state_or_country])
                    else:
                        continue
            except Exception:
                logging.error(traceback.format_exc())
            input_file.close()
            output_file.close()
            return self.output_file


class CSVJSON:
    def __init__(self, csv_file_location):
        self.csv_file_location = os.path.join(BASE_DIR, csv_file_location)
        self.excel_dict_conversion_list = None
        self.json_file_location = os.path.join(MEDIA_ROOT, self.randomword(20) + '.json')

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def convert_csv_to_json(self):
        if self.csv_file_location.split('.')[-1] == 'csv':
            df_json = pd.read_csv(self.csv_file_location)
        else:
            df_json = pd.read_excel(self.csv_file_location)
        self.excel_dict_conversion_list = df_json.to_dict('records')
        return self.excel_dict_conversion_list

    def convert_excel_dict_list_to_json_format(self):
        if self.excel_dict_conversion_list:
            new_dict_list = []
            dict_headers = self.excel_dict_conversion_list[0].keys()
            for dict_item in self.excel_dict_conversion_list:
                new_dict = {}
                for header in dict_headers:
                    if str(dict_item.get(header)) == 'nan':
                        dict_value = None
                    else:
                        dict_value = dict_item.get(header)
                    new_dict[header.lower().replace(' ', '_')] = dict_value
                new_dict_list.append(new_dict)
            with open(self.json_file_location, 'w') as write_file:
                json.dump(new_dict_list, write_file)

            return self.json_file_location

    def to_json(self):
        self.convert_csv_to_json()
        return self.convert_excel_dict_list_to_json_format()
