import datetime

from graphene_django import DjangoObjectType
from .models import TaskModel, OrganizerModel, UserModel, validate, USER_VALIDATION, TASK_VALIDATION, \
    PingModel, get_user_tasks, get_users_related_to_task, GroupModel, MembershipModel, get_user_groups
from graphene import Int, String, Date, Boolean, Field, ObjectType, Mutation, Schema, List


class User(DjangoObjectType):
    email = String(required=True)
    password = String(required=True)
    first_name = String(required=True)
    last_name = String(required=True)
    birthdate = Date(required=True)
    job_title = String(required=True)
    company = String(required=True)
    session_key = String(required=True)
    photo_url = String()

    def resolve_photo_url(self, info):
        return self.photo.url if self.photo else None

    class Meta:
        model = UserModel


class Group(DjangoObjectType):
    name = String(required=True)
    description = String(required=False)
    owner = Field(User, required=True)

    class Meta:
        model = GroupModel


class Membership(DjangoObjectType):
    user = Field(User, required=True)
    group = Field(Group, required=True)

    class Meta:
        model = MembershipModel


class Task(DjangoObjectType):
    name = String(required=True)
    execution_date = Date(required=True)
    deadline = Date(required=True)
    description = String(required=True)
    fruits = String(required=True)
    state = String(required=True)
    author = Field(User, required=True)
    personal_date = Date(required=False)

    class Meta:
        model = TaskModel


class Organizer(DjangoObjectType):
    next_organizer = Field(lambda: Organizer)
    task = Field(Task, required=True)
    user = Field(User, required=True)
    personal_date = Date(required=True)

    class Meta:
        model = OrganizerModel


class Ping(DjangoObjectType):
    task = Field(Task, required=True)
    user_from = Field(User, required=True)
    user_to = Field(User, required=True)
    ping_type = String(required=True)
    message = String(required=False)
    date = Date(required=True)

    class Meta:
        model = PingModel


class Login(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    user = Field(lambda: User)
    ok = Boolean()

    @classmethod
    def mutate(cls, parent, info, email, password):
        user_model = UserModel.objects.filter(email=email, password=password).first()

        if user_model is None:
            return Login(user=None, ok=False)

        user_model.generate_session_key()
        user_model.save()
        return Login(user=user_model, ok=True)


class ValidateName(Mutation):
    class Arguments:
        first_name = String(required=True)
        last_name = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, first_name, last_name):
        ok, error_info = UserModel.verify_not_empty_str(first_name)
        ok, error_info = UserModel.verify_not_empty_str(last_name) if ok else (ok, error_info)
        return ValidateName(ok=ok, error_info=error_info)


class ValidateBirthdate(Mutation):
    class Arguments:
        birthdate = Date(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, birthdate):
        ok, error_info = UserModel.verify_birthdate(birthdate)
        return ValidateBirthdate(ok=ok, error_info=error_info)


class ValidateJob(Mutation):
    class Arguments:
        job_title = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, job_title):
        ok, error_info = UserModel.verify_not_empty_str(job_title)
        return ValidateJob(ok=ok, error_info=error_info)


class ValidateCompany(Mutation):
    class Arguments:
        company = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, company):
        ok, error_info = UserModel.verify_not_empty_str(company)
        return ValidateCompany(ok=ok, error_info=error_info)


class ValidateEmail(Mutation):
    class Arguments:
        email = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, email):
        ok, error_info = UserModel.verify_email(email)
        return ValidateEmail(ok=ok, error_info=error_info)


class ValidatePassword(Mutation):
    class Arguments:
        password = String(required=True)
        repeated_password = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, password, repeated_password):
        ok, error_info = UserModel.verify_password(password)
        ok, error_info = UserModel.verify_password(repeated_password) if ok else (ok, error_info)
        ok, error_info = (False, "passwords are not the same") if ok and password != repeated_password else (
            ok, error_info)
        return ValidatePassword(ok=ok, error_info=error_info)


class Registration(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)
        repeated_password = String(required=True)
        first_name = String(required=True)
        last_name = String(required=True)
        birthdate = Date(required=True)
        job_title = String(required=True)
        company = String(required=True)

    ok = Boolean()
    error_info = String()
    user = Field(lambda: User)

    @classmethod
    def mutate(cls, parent, info, **kwargs):
        user = None
        ok, error_info = validate(USER_VALIDATION, **kwargs)

        password = kwargs.get('password')
        repeated_password = kwargs.get('repeated_password')

        if ok and password != repeated_password:
            ok, error_info = False, "passwords are not the same"
        if not ok:
            return Registration(ok=ok, error_info=error_info, user=user)

        email = kwargs.get('email')
        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        birthdate = kwargs.get('birthdate')
        job_title = kwargs.get('job_title')
        company = kwargs.get('company')

        if ok:
            user = UserModel(first_name=first_name, last_name=last_name, birthdate=birthdate, company=company,
                             email=email, password=password, job_title=job_title)
            user.generate_session_key()
            user.save()
        return Registration(ok=ok, error_info=error_info, user=user)


class UserUpdate(Mutation):
    class Arguments:
        session_key = String(required=True)
        email = String(required=False)
        password = String(required=False)
        first_name = String(required=False)
        last_name = String(required=False)
        birthdate = Date(required=False)
        job_title = String(required=False)
        company = String(required=False)

    ok = Boolean()
    error_info = String()
    user = Field(lambda: User)

    @classmethod
    def mutate(cls, parent, info, session_key, **kwargs):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return UserUpdate(ok=False, error_info="invalid session key", user=None)

        ok, error_info = validate(USER_VALIDATION, **kwargs)
        if not ok:
            return UserUpdate(ok=ok, error_info=error_info, user=user)

        user.__dict__.update(
            (key, val) for key, val in kwargs.items() if val is not None and key in USER_VALIDATION.keys()
        )
        user.save()
        return UserUpdate(ok=ok, error_info=error_info, user=user)


class AddTask(Mutation):
    class Arguments:
        session_key = String(required=True)
        name = String(required=True)
        execution_date = Date(required=True)
        users_id = List(Int)
        deadline = Date(required=False)
        description = String(required=False)
        fruits = String(required=False)
        group_id = Int(required=False)

    ok = Boolean()
    error_info = String()
    user = Field(lambda: User)
    prev_organizer = Field(lambda: Organizer)
    next_organizer = Field(lambda: Organizer)
    organizer = Field(lambda: Organizer)
    task = Field(lambda: Task)
    group = Field(lambda: Group)

    @classmethod
    def mutate(cls, parent, info, session_key, **kwargs):
        author = UserModel.authenticate_session_key(session_key)
        if author is None:
            return AddTask(ok=False, error_info="invalid session key", task=None)

        ok, error_info = validate(TASK_VALIDATION, **kwargs)
        if not ok:
            return AddTask(ok=ok, error_info=error_info, task=None)

        name = kwargs.get('name')
        execution_date = kwargs.get('execution_date')
        deadline = kwargs.get('deadline', execution_date)
        users_id = kwargs.get('users_id', [])
        description = kwargs.get('description', "")
        fruits = kwargs.get('fruits', "")
        group_id = kwargs.get('group_id', None)

        # only one of options: group, chosen users
        if users_id != [] and group_id is not None:
            return AddTask(ok=False, error_info="not possible to add task to group and additional users", task=None)

        group = None
        if group_id is not None:
            group = GroupModel.get_group_by_id(group_id)
            if group is None or MembershipModel.get_membership(author, group) is None:
                return AddTask(ok=False, error_info="invalid group id", task=None)

        users = []
        if group is not None:
            # all members will get a task, now author is owner of group
            users = MembershipModel.get_group_members(group)
            author = group.owner
        else:
            # check are ids valid, preparing all to receive task
            users = [author]
            for user_id in users_id:
                user = UserModel.get_user_by_id(user_id=user_id)
                if user is None:
                    return AddTask(ok=False, error_info="invalid one of users id", task=None)
                users.append(user)

        # creating task
        task = TaskModel(name=name, execution_date=execution_date, deadline=deadline, description=description,
                         fruits=fruits, state='In progress', author=author, personal_date=execution_date, group=group)
        task.save()

        # organizer for creator + users from group
        for user in users:
            last_organizer = OrganizerModel.last_user_organizer(execution_date, user)
            next_organizer = last_organizer.next_organizer if last_organizer is not None else OrganizerModel.first_user_organizer(user)

            organizer = OrganizerModel(next_organizer=None, task=task, user=user, personal_date=execution_date)
            organizer.save()

            if last_organizer is not None:
                last_organizer.next_organizer = organizer
                last_organizer.save()

            organizer.next_organizer = next_organizer
            organizer.save()

            message = 'You were added to task.' if user != author else 'You created task.'
            if group is not None:
                message = f'New task in group {group.name}.'

            ping = PingModel(user_from=author, user_to=user, task=task, ping_type='New task', message=message, date=datetime.datetime.now())
            ping.save()

        return AddTask(ok=ok, error_info=error_info, task=task)


class UpdateTask(Mutation):
    class Arguments:
        session_key = String(required=True)
        task_id = Int(required=True)
        name = String(required=False)
        execution_date = Date(required=False)
        deadline = Date(required=False)
        description = String(required=False)
        fruits = String(required=False)
        state = String(required=False)

    ok = Boolean()
    error_info = String()
    user = Field(lambda: User)
    task = Field(lambda: Task)
    organizer = Field(lambda: Organizer)

    @classmethod
    def mutate(cls, parent, info, session_key, task_id, **kwargs):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return UpdateTask(ok=False, error_info="invalid session key", task=None)

        task = TaskModel.get_task_by_id(task_id=task_id)
        if task is None:
            return UpdateTask(ok=False, error_info="invalid task id", task=None)

        organizer = OrganizerModel.get_organizer_of_task(task=task, user=user)
        if organizer is None:
            return UpdateTask(ok=False, error_info="Invalid task id", task=None)

        ok, error_info = validate(TASK_VALIDATION, **kwargs)
        if not ok:
            return UpdateTask(ok=ok, error_info=error_info, task=None)

        if user != task.author:
            message = PingModel.get_message_change_request(kwargs)
            ping = PingModel(user_from=user, user_to=task.author, task=task, ping_type='Change request',
                             message=message, date=datetime.datetime.now())
            ping.save()
            return UpdateTask(ok=True, error_info=None, task=None)

        task.__dict__.update(
            (key, val) for key, val in kwargs.items() if val is not None and key in TASK_VALIDATION.keys()
        )
        task.save()

        message = PingModel.get_message_updated_task(kwargs)
        for user in get_users_related_to_task(task):
            ping = PingModel(user_from=task.author, user_to=user, task=task, ping_type='Updated task',
                             message=message, date=datetime.datetime.now())
            ping.save()

        return UpdateTask(ok=ok, error_info=error_info, task=task)


class ChangePriorityTask(Mutation):
    class Arguments:
        session_key = String(required=True)
        previous_task_id = Int()
        task_id = Int(required=True)
        personal_date = Date(required=False)

    ok = Boolean()
    error_info = String()
    tasks = List(Task)

    @classmethod
    def mutate(cls, parent, info, session_key, task_id, previous_task_id=None, personal_date=None):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return ChangePriorityTask(ok=False, error_info="invalid session key")

        if previous_task_id == task_id:
            return ChangePriorityTask(ok=False, error_info="invalid task id")

        task = TaskModel.get_task_by_id(task_id=task_id)
        if task is None:
            return ChangePriorityTask(ok=False, error_info="invalid task id")

        organizer = OrganizerModel.get_organizer_of_task(task=task, user=user)
        if organizer is None:
            return ChangePriorityTask(ok=False, error_info="invalid task id")

        previous_task = None
        if previous_task_id is not None:
            previous_task = TaskModel.get_task_by_id(task_id=previous_task_id)
            if previous_task is None:
                return ChangePriorityTask(ok=False, error_info="invalid task id")

        previous_organizer = None
        if previous_task_id is not None:
            previous_organizer = OrganizerModel.get_organizer_of_task(task=previous_task, user=user)
            if previous_organizer is None:
                return ChangePriorityTask(ok=False, error_info="invalid task id")

        if personal_date is not None:
            if personal_date < datetime.date.today():
                return ChangePriorityTask(ok=False, error_info="invalid personal date")

        organizer.personal_date = personal_date
        organizer.save()

        first = OrganizerModel.first_user_organizer(user)
        if first == organizer:
            first = first.next_organizer

        def prev_org(org):
            return org.get_previous_organizer() if org else None

        def next_org(org):
            return org.next_organizer if org else None

        def remove_org(org):
            prev_o = prev_org(org)
            next_o = next_org(org)
            if org is not None:
                org.next_organizer = None
                org.save()
            if prev_o is not None:
                prev_o.next_organizer = next_o
                prev_o.save()

        def add_org(org, prev_o):
            assert org is not None
            next_o = next_org(prev_o) if prev_o else first
            if prev_o is not None:
                prev_o.next_organizer = None
                prev_o.save()
            org.next_organizer = next_o
            org.save()
            if prev_o is not None:
                prev_o.next_organizer = org
                prev_o.save()

        remove_org(organizer)
        organizer.refresh_from_db()
        if previous_organizer is not None:
            previous_organizer.refresh_from_db()
        add_org(organizer, previous_organizer)

        tasks = []
        first_organizer = OrganizerModel.first_user_organizer(user=user)
        while first_organizer is not None:
            task = first_organizer.task
            task.personal_date = first_organizer.personal_date
            tasks.append(task)
            first_organizer = first_organizer.next_organizer

        return ChangePriorityTask(ok=True, error_info=None, tasks=tasks)


class SendPing(Mutation):
    class Arguments:
        session_key = String(required=True)
        other_id = Int(required=True)
        task_id = Int(required=True)
        ping_type = String(required=True)
        message = String(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, other_id, task_id, ping_type, message):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return SendPing(ok=False, error_info="invalid session key")

        other_user = UserModel.get_user_by_id(other_id)
        if user.id == other_id or other_user is None:
            return SendPing(ok=False, error_info="invalid id of other user")

        task = TaskModel.get_task_by_id(task_id=task_id)
        if task is None:
            return SendPing(ok=False, error_info="invalid task id")

        if not PingModel.verify_ping_type(ping_type=ping_type):
            return SendPing(ok=False, error_info="invalid ping type")

        if PingModel.ping_exists(task=task, user_from=user, user_to=other_user, ping_type=ping_type):
            return SendPing(ok=False, error_info="similar ping exists")

        PingModel(task=task, user_from=user, user_to=other_user, ping_type=ping_type, message=message,
                  date=datetime.date.today()).save()

        return SendPing(ok=True, error_info=None)


class SetPingEnded(Mutation):
    class Arguments:
        session_key = String(required=True)
        ping_id = Int(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, ping_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return SetPingEnded(ok=False, error_info="invalid session key")

        ping = PingModel.get_ping_by_id(ping_id)
        if ping is None or ping.user_to != user:
            return SetPingEnded(ok=False, error_info="invalid ping id")

        ping.ping_type = 'Ended'
        ping.save()
        return SetPingEnded(ok=True, error_info=None)


class AddGroup(Mutation):
    class Arguments:
        session_key = String(required=True)
        name = String(required=True)
        description = String(required=False)

    ok = Boolean()
    error_info = String()
    group = Field(lambda: Group)

    @classmethod
    def mutate(cls, parent, info, session_key, name, description=None):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return AddGroup(ok=False, error_info="invalid session key", group=None)

        ok, error_info = UserModel.verify_not_empty_str(name)
        if not ok:
            return AddGroup(ok=False, error_info=error_info, group=None)

        group = GroupModel(name=name, description=description, owner=user)
        group.save()

        membership = MembershipModel(user=user, group=group)
        membership.save()

        return AddGroup(ok=True, error_info=None, group=group)


class AddGroupMember(Mutation):
    class Arguments:
        session_key = String(required=True)
        group_id = Int(required=True)
        user_id = Int(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, group_id, user_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return AddGroupMember(ok=False, error_info="invalid session key")

        group = GroupModel.get_group_by_id(group_id=group_id)
        if group is None:
            return AddGroupMember(ok=False, error_info="invalid group id")

        if group.owner != user:
            return AddGroupMember(ok=False, error_info="invalid group id")

        user = UserModel.get_user_by_id(user_id)
        if user is None:
            return AddGroupMember(ok=False, error_info="invalid user id")

        if MembershipModel.get_membership(user=user, group=group) is not None:
            return AddGroupMember(ok=False, error_info="user is in group")

        membership = MembershipModel(user=user, group=group)
        membership.save()

        tasks = TaskModel.get_group_tasks(group=group)
        for task in tasks:
            last_organizer = OrganizerModel.last_user_organizer(task.execution_date, user)
            next_organizer = last_organizer.next_organizer if last_organizer is not None else OrganizerModel.first_user_organizer(
                user)

            organizer = OrganizerModel(next_organizer=None, task=task, user=user, personal_date=task.execution_date)
            organizer.save()

            if last_organizer is not None:
                last_organizer.next_organizer = organizer
                last_organizer.save()

            organizer.next_organizer = next_organizer
            organizer.save()

        return AddGroupMember(ok=True, error_info=None)


class LeaveGroup(Mutation):
    class Arguments:
        session_key = String(required=True)
        group_id = Int(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, group_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return LeaveGroup(ok=False, error_info="invalid session key")

        group = GroupModel.get_group_by_id(group_id=group_id)
        if group is None:
            return LeaveGroup(ok=False, error_info="invalid group id")

        membership = MembershipModel.get_membership(user=user, group=group)
        if membership is None:
            return LeaveGroup(ok=False, error_info="invalid group id")

        membership.delete()

        tasks = TaskModel.get_group_tasks(group)
        for task in tasks:
            organizer = OrganizerModel.get_organizer_of_task(task=task, user=user)
            next_organizer = organizer.next_organizer
            previous_organizer = organizer.get_previous_organizer()

            organizer.delete()

            if previous_organizer is not None:
                previous_organizer.next_organizer = next_organizer
                previous_organizer.save()
        return LeaveGroup(ok=True, error_info="")


class DeleteGroupMember(Mutation):
    class Arguments:
        session_key = String(required=True)
        group_id = Int(required=True)
        user_id = Int(required=True)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, group_id, user_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return DeleteGroupMember(ok=False, error_info="invalid session key")

        group = GroupModel.get_group_by_id(group_id=group_id)
        if group is None:
            return DeleteGroupMember(ok=False, error_info="invalid group id")

        if group.owner != user:
            return DeleteGroupMember(ok=False, error_info="invalid group id")

        user = UserModel.get_user_by_id(user_id)
        if user is None:
            return DeleteGroupMember(ok=False, error_info="invalid user id")

        membership = MembershipModel.get_membership(user=user, group=group)
        if membership is None:
            return DeleteGroupMember(ok=False, error_info="invalid user id")

        membership.delete()

        tasks = TaskModel.get_group_tasks(group)
        for task in tasks:
            organizer = OrganizerModel.get_organizer_of_task(task=task, user=user)
            next_organizer = organizer.next_organizer
            previous_organizer = organizer.get_previous_organizer()

            organizer.delete()

            if previous_organizer is not None:
                previous_organizer.next_organizer = next_organizer
                previous_organizer.save()
        return DeleteGroupMember(ok=True, error_info="")


class ShareTask(Mutation):
    class Arguments:
        session_key = String(required=True)
        task_id = Int(required=True)
        group_id = Int(required=False)
        user_id = Int(required=False)

    ok = Boolean()
    error_info = String()

    @classmethod
    def mutate(cls, parent, info, session_key, task_id, group_id=None, user_id=None):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return ShareTask(ok=False, error_info="invalid session key")

        task = TaskModel.get_task_by_id(task_id)
        if task is None:
            return ShareTask(ok=False, error_info="invalid task id")

        if OrganizerModel.get_organizer_of_task(task=task, user=user) is None:
            return ShareTask(ok=False, error_info="invalid task id")

        if (group_id is None and user_id is None) or (group_id is not None and user_id is not None):
            return ShareTask(ok=False, error_info="must one of two: group id, user id be provided")

        if group_id is not None:
            group = GroupModel.get_group_by_id(group_id=group_id)
            if group is None:
                return ShareTask(ok=False, error_info="invalid group id")

            membership = MembershipModel.get_membership(user=user, group=group)
            if membership is None:
                return ShareTask(ok=False, error_info="invalid group id")

            task_users = get_users_related_to_task(task=task)
            group_users = MembershipModel.get_group_members(group=group)
            if all(usr in group_users for usr in task_users):

                task.group = group
                task.author = group.owner
                task.save()

                diff = [usr for usr in group_users if usr not in task_users]

                for usr in diff:
                    last_organizer = OrganizerModel.last_user_organizer(task.execution_date, usr)
                    next_organizer = last_organizer.next_organizer if last_organizer is not None else OrganizerModel.first_user_organizer(usr)

                    organizer = OrganizerModel(next_organizer=None, task=task, user=usr,
                                               personal_date=task.execution_date)
                    organizer.save()

                    if last_organizer is not None:
                        last_organizer.next_organizer = organizer
                        last_organizer.save()

                    organizer.next_organizer = next_organizer
                    organizer.save()

                    message = f'Task shared with group {group.name} by {user.first_name}.'

                    ping = PingModel(user_from=user, user_to=usr, task=task, ping_type='New task', message=message,
                                     date=datetime.datetime.now())
                    ping.save()

                return ShareTask(ok=True, error_info=None)

            return ShareTask(ok=False, error_info="this task can't be shared to that group")

        else:
            usr = UserModel.get_user_by_id(user_id)
            if usr is None:
                return ShareTask(ok=False, error_info="invalid user id")

            if task.group is not None:
                return ShareTask(ok=False, error_info="invalid task id")

            last_organizer = OrganizerModel.last_user_organizer(task.execution_date, usr)
            next_organizer = last_organizer.next_organizer if last_organizer is not None else OrganizerModel.first_user_organizer(usr)

            organizer = OrganizerModel(next_organizer=None, task=task, user=usr, personal_date=task.execution_date)
            organizer.save()

            if last_organizer is not None:
                last_organizer.next_organizer = organizer
                last_organizer.save()

            organizer.next_organizer = next_organizer
            organizer.save()

            message = f'{user.first_name} shared task with You.'
            ping = PingModel(user_from=user, user_to=usr, task=task, ping_type='New task', message=message,
                             date=datetime.datetime.now())
            ping.save()

            return ShareTask(ok=True, error_info=None)


class Query(ObjectType):
    users = List(User, args={
        'id': Int(),
        'first_name': String(),
        'last_name': String(),
        'email': String(),
        'birthdate': Date(),
        'job_title': String(),
        'company': String(),
        'session_key': String()
    })

    @staticmethod
    def resolve_users(parent, info, **kwargs):
        users = UserModel.objects
        for key, val in kwargs.items():
            users = users.filter(**{key: val})
        return users.all()

    user_tasks = List(Task, args={'session_key': String(required=True)})

    @staticmethod
    def resolve_user_tasks(parent, info, session_key):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return []
        return get_user_tasks(user=user)

    other_user_tasks = List(Task, args={'session_key': String(required=True), 'other_id': Int(required=True)})

    @staticmethod
    def resolve_other_user_tasks(parent, info, session_key, other_id):
        user = UserModel.authenticate_session_key(session_key)
        other_user = UserModel.get_user_by_id(user_id=other_id)
        if user is None or other_user is None:
            return []

        tasks = get_user_tasks(user=user)
        other_tasks = get_user_tasks(user=other_user)
        return [other_task for other_task in other_tasks if other_task not in tasks]  # we will save orderly

    ping_list = List(Ping, args={'session_key': String(required=True)})

    common_user_tasks = List(Task, args={'session_key': String(required=True), 'other_id': Int(required=True)})

    @staticmethod
    def resolve_common_user_tasks(parent, info, session_key, other_id):
        user = UserModel.authenticate_session_key(session_key)
        other_user = UserModel.get_user_by_id(user_id=other_id)
        if user is None or other_user is None:
            return []

        tasks = get_user_tasks(user=user)
        other_tasks = get_user_tasks(user=other_user)
        return [other_task for other_task in other_tasks if other_task in tasks]

    @staticmethod
    def resolve_ping_list(parent, info, session_key):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return []

        pings = PingModel.get_user_ping_list(user=user)
        return sorted(pings, key=lambda ping: ping.date)

    ping_data_for_request = Field(Ping, args={'session_key': String(required=True), 'task_id': Int(required=True)})

    @staticmethod
    def resolve_ping_data_for_request(parent, info, session_key, task_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return None

        task = TaskModel.get_task_by_id(task_id=task_id)
        if task is None:
            return None

        author = task.author
        ping_type = 'Delay request' if OrganizerModel.get_organizer_of_task(task, user) else 'Progress request'
        return PingModel(task=task, user_from=user, user_to=author, ping_type=ping_type, date=None, message=None)

    ping_data_for_answer = Field(Ping, args={'session_key': String(required=True), 'ping_id': Int(required=True)})

    @staticmethod
    def resolve_ping_data_for_answer(parent, info, session_key, ping_id):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return None

        ping = PingModel.get_ping_by_id(ping_id=ping_id)
        if ping is None:
            return None

        if ping.user_to != user:
            return None

        ping_type = 'Answer ping'
        return PingModel(task=ping.task, user_from=user, user_to=ping.user_from, ping_type=ping_type, date=None,
                         message=None)

    groups = List(Group, args={'id': Int(), 'name': String()})

    @staticmethod
    def resolve_groups(parent, info, **kwargs):
        groups = GroupModel.objects
        for key, val in kwargs.items():
            groups = groups.filter(**{key: val})
        return groups.all()

    user_groups = List(Group, args={'session_key': String(required=True)})

    @staticmethod
    def resolve_user_groups(parent, info, session_key):
        user = UserModel.authenticate_session_key(session_key)
        if user is None:
            return []
        return get_user_groups(user)

    task = Field(Task)
    organizer = Field(Organizer)


class Mutations(ObjectType):
    login = Login.Field()
    validate_name = ValidateName.Field()
    validate_birthdate = ValidateBirthdate.Field()
    validate_job_title = ValidateJob.Field()
    validate_company = ValidateCompany.Field()
    validate_email = ValidateEmail.Field()
    validate_password = ValidatePassword.Field()
    registration = Registration.Field()
    user_update = UserUpdate.Field()
    add_task = AddTask.Field()
    update_task = UpdateTask.Field()
    change_priority_task = ChangePriorityTask.Field()
    send_ping = SendPing.Field()
    set_ping_ended = SetPingEnded.Field()
    add_group = AddGroup.Field()
    add_group_member = AddGroupMember.Field()
    leave_group = LeaveGroup.Field()
    delete_group_member = DeleteGroupMember.Field()
    share_task = ShareTask.Field()


schema = Schema(query=Query, mutation=Mutations)
