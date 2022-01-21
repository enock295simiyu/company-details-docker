import logging
import os
import traceback

import bigjson
from celery import shared_task

from company_details.settings import BASE_DIR
from core.core_handler import CoreHandler
from core.models import CoreManager

log = logging.getLogger(__name__)


@shared_task
def add(x, y):
    return x + y


@shared_task
def populate_company_data_model_async(data):
    """
    This function populates the contents of uploaded json data to the model
    :param data: {'json_file': The File object that contains json upload file,'json_location_url': The file location of a
    json file}
    :return:
    """
    log.info('Asynchronous task has been started')

    log.info('Starting populating company data model')
    if data.get('json_location_url'):
        json_file_path = data.get('json_location_url')
    else:
        json_file = CoreHandler().get_file_by_id({'json_file_id': data.get('json_file_id')})
        json_file_path = os.path.join(BASE_DIR, json_file.json_file.url[1:])

    with open(json_file_path, 'rb') as f:
        all_company_data = bigjson.load(f)
        number_updated = 0
        number_created = 0
        total_count = len(all_company_data)
        log.info(f'Total number of items is {str(total_count)}')
        for counter, company_data in enumerate(all_company_data):
            log.info(f'Processing item: {counter} out of {str(total_count)}')
            company_data = company_data.to_python()

            if counter == 0:
                log.info('Company data:1......')
            elif counter % 100 == 0:
                log.info('Company data:' + str(counter * 100) + '....')
            try:
                if company_data.get('_source'):
                    return_data = CoreManager().old_update_function(company_data=company_data.get('_source'),
                                                                    upload_details_id=data.get('upload_details_id'))
                    if return_data:
                        number_created += return_data[0]
                        number_updated += return_data[1]
                else:
                    return_data = CoreManager().new_update_function(company_data=company_data,
                                                                    upload_details_id=data.get('upload_details_id'))
                    if return_data:
                        number_created += return_data[0]
                        number_updated += return_data[1]
            except Exception:
                log.info(f'An error occurred while processing item: {counter} out of {str(total_count)}')
                log.info(f'This is the data: {str(company_data)}')
                logging.error(traceback.format_exc())

    log.info('Completed adding json data to company data model')
    return number_created, number_updated
