from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from config_master import PREMIUM_PLAN
from payment.models import UserPlan


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = PhoneNumberField()
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def is_premium_user(self):
        """
        This function checks if a user is a premium user or not
        :return: Boolean value
        """
        user_plan = UserPlan.objects.get(user=self.user)
        if not user_plan.payment_plan:
            return False
        else:
            if user_plan.payment_plan.plan_type == PREMIUM_PLAN:
                return True
            else:
                return False

    def total_viewed_data(self):
        """
        This function returns the total number of company data that has been viewed by a user
        :return: Boolean value
        """
        user_plan = UserPlan.objects.get(user=self.user)
        return user_plan.viewed_company_data.count()

    def current_plan(self):
        """
        This function returns the string name of the current user plan
        :return: STR value
        """
        user_plan = UserPlan.objects.get(user=self.user)
        if user_plan.payment_plan:
            return user_plan.payment_plan.name
        else:
            return 'No Plan'

    def remaining_credits(self):
        """
        This function returns the total number of remaining credits a user is still having
        :return: INT
        """
        user_plan = UserPlan.objects.get(user=self.user)
        return user_plan.credits_remaining


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This siganl creates a profile instance for a user when the user account is created
    :param sender:
    :param instance: The user object
    :param created: Boolean value
    :param kwargs:
    :return:
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        Profile.objects.get(user=instance).save()
    except:
        Profile.objects.create(user=instance)


class AccountsManager(object):
    def countDigit(self, n):
        count = 0
        while n != 0:
            n //= 10
            count += 1
        return count

    def get_all_staff(self):
        return User.objects.all().order_by('-id')

    def get_user_by_id(self, data):
        return User.objects.get(id=data.get('user_id'))

    def update_user_information(self, data):
        """
        This function updates a specific users information
        :param data: {'user':The User object,'first_name': First name of the user, 'last_name':The last name value of
        the user, 'phone_number': Phone number value of the user}
        :return:
        """
        user = data.get('user')

        user_profile = Profile.objects.get(user=user)
        initial_phone_number = user_profile.phone_number
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.save()
        if initial_phone_number != data.get('phone_number'):
            user_profile.is_phone_verified = False
        user_profile.phone_number = data.get('phone_number')
        user_profile.save()
        return user

    def verify_phonenumber(self, user):
        """
        :param user:
        This function verifies the phone of a user
        :return:
        """
        user_profile = Profile.objects.get(user=user)
        user_profile.is_phone_verified = True
        user_profile.save()
        return user


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    This signal created a user plan instance with 25 credits when a when a user account is created
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        UserPlan.objects.create(user=instance, credits_remaining=25, created_by=instance.username)
