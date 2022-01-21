from core.models import CoreManager


class CoreHandler:
    def __init__(self):
        self.core_manager = CoreManager()

    def add_json_file_to_file_object(self,data):
        return self.core_manager.add_json_file_to_file_object(data)

    def create_file(self, data):
        return self.core_manager.create_file(data)

    def get_all_company_source_objects(self, data):
        return self.core_manager.get_all_company_source_objects(data)

    def get_company_source_by_source_id(self, data):
        return self.core_manager.get_company_source_by_source_id(data)

    def filter_company_source_objects(self, data):
        return self.core_manager.filter_company_source_objects(data)

    def filter_company_source_objects_according_to_siniority(self, data):
        return self.core_manager.filter_company_source_objects_according_to_siniority(data)

    def filter_company_source_objects_according_to_country(self, data):
        return self.core_manager.filter_company_source_objects_according_to_country(data)

    def filter_company_source_objects_according_to_revenue_range(self, data):
        return self.core_manager.filter_company_source_objects_according_to_revenue_range(data)

    def return_all_data_count(self):
        return self.core_manager.return_all_data_count()

    def get_email_phone_by_company_data_id(self, data):
        return self.core_manager.get_email_phone_by_company_data_id(data)

    def create_fields_mapping(self, data):
        return self.core_manager.create_fields_mapping(data)

    def filter_company_data_json(self, data):
        return self.core_manager.filter_company_data_json(data)

    def get_page_metrics_for_all_company_data(self):
        return self.core_manager.get_page_metrics_for_all_company_data()

    def convert_company_source_data_into_json_queryset(self, data):
        return self.core_manager.convert_company_source_data_into_json_queryset(data)

    def get_file_by_id(self, data):
        return self.core_manager.get_file_by_id(data)

    def add_task_id_to_file(self, data):
        return self.core_manager.add_task_id_to_file(data)

    def get_all_file_uploads(self):
        return self.core_manager.get_all_file_uploads()

    def check_upload_status(self):
        return self.core_manager.check_upload_status()

    def update_upload_status(self):
        return self.core_manager.update_upload_status()

    def updated_company_source_populate(self):
        pass

    def main_company_data_filter(self,data):
        return self.core_manager.main_company_data_filter(data)
