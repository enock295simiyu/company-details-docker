import os

FREE_MEMBER = 'FREE_MEMBER'
REGULAR_MEMBER = 'REGULAR_MEMBER'
PREMIUM_MEMBER = 'PREMIUM_MEMBER'
ADMIN_MEMBER = 'ADMIN_MEMBER'
user_plan_choices = (
    (FREE_MEMBER, FREE_MEMBER),
    (REGULAR_MEMBER, REGULAR_MEMBER),
    (PREMIUM_MEMBER, PREMIUM_MEMBER),
    (ADMIN_MEMBER, ADMIN_MEMBER),
)
PREMIUM_PLAN = 'PREMIUM_PLAN'
REGULAR_PLAN = 'REGULAR_PLAN'
plan_type_choices = (
    (REGULAR_PLAN, REGULAR_PLAN),
    (REGULAR_PLAN, REGULAR_PLAN),
)
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

STATUS_UPLOADED = 'UPLOADED'
STATUS_PROCESSING = 'PROCESSING'
STATUS_COMPLETED = 'COMPLETED'

file_status_choices = (
    (STATUS_UPLOADED, STATUS_UPLOADED),
    (STATUS_PROCESSING, STATUS_PROCESSING),
    (STATUS_COMPLETED, STATUS_COMPLETED),
)
