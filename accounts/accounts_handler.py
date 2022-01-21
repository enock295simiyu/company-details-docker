from accounts.models import AccountsManager


class AccountsHandler(object):
    def __init__(self):
        self.accounts_obj = AccountsManager()

    def get_all_staff(self):
        return self.accounts_obj.get_all_staff()

    def get_user_by_id(self, data):
        return self.accounts_obj.get_user_by_id(data)

    def update_user_information(self, data):
        return self.accounts_obj.update_user_information(data)

    def verify_phonenumber(self, user):
        return self.accounts_obj.verify_phonenumber(user)
