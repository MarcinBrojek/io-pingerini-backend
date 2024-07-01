import datetime
import re
import string

from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string

_SESSION_KEY_LEN = 64
_EMAIL_PATTERN = re.compile("^[a-zA-Z0-9\._]+[@]+([a-zA-Z0-9\._]*)+[a-zA-Z0-9]+[.]\w{2,4}$")
_PASSWORD_CHARACTERS = list(string.ascii_letters) + list(string.digits) + ['_', '-']


class UserModel(models.Model):
    session_key = models.CharField(max_length=_SESSION_KEY_LEN)
    email = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    birthdate = models.DateField()
    job_title = models.CharField(max_length=64)
    company = models.CharField(max_length=64)
    photo = models.ImageField(null=True)

    def generate_session_key(self):
        self.session_key = get_random_string(_SESSION_KEY_LEN)
        return self.session_key

    @staticmethod
    def authenticate_session_key(key):
        query = UserModel.objects.filter(session_key=key).all()
        return query.first() if query else None

    @staticmethod
    def get_user_by_id(user_id):
        query = UserModel.objects.filter(id=user_id).all()
        return query.first() if query else None

    @staticmethod
    def verify_not_empty_str(s):
        if len(s) <= 0 or 64 < len(s):
            return False, "expected length [1..64]"
        return True, None

    @staticmethod
    def verify_email(email):
        not_empty = UserModel.verify_not_empty_str(email)
        if not not_empty[0]:
            return not_empty
        if not re.match(pattern=_EMAIL_PATTERN, string=email):
            return False, "wrong email address format"
        if len(UserModel.objects.filter(email=email)) != 0:
            return False, "email already used"
        return True, None

    @staticmethod
    def verify_password(password):
        if len(password) < 8 or 64 < len(password):
            return False, "expected length [8..64]"
        if not any(c in string.ascii_uppercase for c in password) or \
                not any(c in string.ascii_lowercase for c in password) or \
                not any(c in string.digits for c in password) or \
                any(c not in _PASSWORD_CHARACTERS for c in password):
            return False, "expected at least one: uppercase letter, lowercase letter and digit; all characters have to be one of: 'a'-'z', 'A'-'Z', '0'-'9', '_', '-'"
        return True, None

    @staticmethod
    def verify_birthdate(date):
        if date > datetime.date.today():
            return False, "wrong birthdate"
        return True, None


class GroupModel(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False)

    @staticmethod
    def get_group_by_id(group_id):
        query = GroupModel.objects.filter(id=group_id).all()
        return query.first() if query else None


class MembershipModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False)
    group = models.ForeignKey(GroupModel, on_delete=models.CASCADE, null=False)

    @staticmethod
    def get_membership(user, group):
        query = MembershipModel.objects.filter(user=user, group=group).all()
        return query.first() if query else None

    @staticmethod
    def get_group_members(group):
        query = MembershipModel.objects.filter(group=group).all()
        return [] if not query else [membership.user for membership in query]


class TaskModel(models.Model):
    name = models.CharField(max_length=64)
    execution_date = models.DateField()
    deadline = models.DateField()
    description = models.TextField()
    fruits = models.TextField()
    state = models.TextField(null=False)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False)
    personal_date = models.DateField()
    group = models.ForeignKey(GroupModel, on_delete=models.CASCADE, null=True)

    @staticmethod
    def verify_not_empty_str(s):
        if len(s) <= 0 or 64 < len(s):
            return False, "expected length [1..64]"
        return True, None

    @staticmethod
    def verify_future_date(date):
        if date < datetime.date.today():
            return False, "wrong date"
        return True, None

    @staticmethod
    def get_task_by_id(task_id):
        query = TaskModel.objects.filter(id=task_id).all()
        return query.first() if query else None

    @staticmethod
    def verify_state(state):
        if state not in ['In progress', 'Done']:
            return False, "wrong state"
        return True, None

    @staticmethod
    def get_group_tasks(group):
        query = TaskModel.objects.filter(group=group).all()
        return [] if not query else [task for task in query]


class OrganizerModel(models.Model):
    next_organizer = models.OneToOneField('self', on_delete=models.SET_NULL, null=True)
    task = models.ForeignKey(TaskModel, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False)
    personal_date = models.DateField()

    def get_previous_organizer(self):
        self.refresh_from_db()
        if not hasattr(self, 'organizermodel'):
            return None
        return self.organizermodel

    @staticmethod
    def first_user_organizer(user):
        query = OrganizerModel.objects.filter(user=user).filter(organizermodel=None).all()
        if not query:
            return None
        return query.first()

    @staticmethod
    def last_user_organizer(date, user):
        query = OrganizerModel.objects.filter(user=user).filter(personal_date__lte=date).filter(Q(next_organizer__personal_date__gt=date) | Q(next_organizer__personal_date__isnull=True)).all()
        if not query:
            return None
        return query.first()

    @staticmethod
    def get_organizer_of_task(task, user):
        query = OrganizerModel.objects.filter(task=task, user=user).all()
        return query.first() if query else None


class PingModel(models.Model):
    task = models.ForeignKey(TaskModel, on_delete=models.CASCADE, null=False)
    user_from = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False, related_name='user_from')
    user_to = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=False, related_name='user_to')
    ping_type = models.TextField(null=False)
    message = models.TextField(null=True)
    date = models.DateTimeField(null=True)

    @staticmethod
    def get_user_ping_list(user):
        query = PingModel.objects.filter(user_to=user).all()
        return list(query) if query else []

    @staticmethod
    def verify_ping_type(ping_type):
        return ping_type in ['Progress request', 'Delay request', 'Change request',
                             'Answer ping', 'New task', 'Updated task', 'Ended']

    @staticmethod
    def get_ping_by_id(ping_id):
        query = PingModel.objects.filter(id=ping_id).all()
        return query.first() if query else None

    @staticmethod
    def ping_exists(task, user_from, user_to, ping_type):
        query = PingModel.objects.filter(task=task, user_from=user_from, user_to=user_to, ping_type=ping_type).all()
        return True if query else False

    @staticmethod
    def get_message_change_request(kwargs):
        msg = ''
        for key, val in kwargs.items():
            msg += 'request change' + key + ': ' + val + '\n'
        if msg == '':
            msg = 'request nothing'
        return msg

    @staticmethod
    def get_message_updated_task(kwargs):
        msg = ''
        for key, val in kwargs.items():
            msg += 'updated filed' + key + ': ' + val + '\n'
        if msg == '':
            msg = 'updated nothing'
        return msg


USER_VALIDATION = {
    'first_name': UserModel.verify_not_empty_str,
    'last_name': UserModel.verify_not_empty_str,
    'job_title': UserModel.verify_not_empty_str,
    'company': UserModel.verify_not_empty_str,
    'email': UserModel.verify_email,
    'birthdate': UserModel.verify_birthdate,
    'password': UserModel.verify_password,
    'repeated_password': UserModel.verify_password
}

TASK_VALIDATION = {
    'name': TaskModel.verify_not_empty_str,
    'execution_date': TaskModel.verify_future_date,
    'deadline': TaskModel.verify_future_date,
    'users_id': (lambda x: (True, None)),
    'description': (lambda x: (True, None)),
    'fruits': (lambda x: (True, None)),
    'state': TaskModel.verify_state,
    'group_id': (lambda x: (True, None))
}


# stops on the first error
def validate(validation_dict, **kwargs):
    ok, error_info = True, None
    for key, val in kwargs.items():
        if ok:
            ok, error_info = validation_dict[key](val)
    return ok, error_info


# get list of ordered tasks
def get_user_tasks(user):
    tasks = []
    first_organizer = OrganizerModel.first_user_organizer(user=user)
    while first_organizer is not None:
        task = first_organizer.task
        task.personal_date = first_organizer.personal_date
        tasks.append(task)
        first_organizer = first_organizer.next_organizer
    return tasks


# get list of users related to task
def get_users_related_to_task(task):
    organizers = OrganizerModel.objects.filter(task=task).all()
    if not organizers:
        return []
    return [organizer.user for organizer in organizers]


# get user groups
def get_user_groups(user):
    memberships = MembershipModel.objects.filter(user=user).all()
    if not memberships:
        return []
    return [membership.group for membership in memberships]
