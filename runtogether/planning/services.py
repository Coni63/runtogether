import datetime

from planning.models import Absence
from accounts.models import User


def __generate_list_of_dates(date_start: datetime.date, date_end: datetime.date):
    if date_start and date_end:
        # the library provides dates sorted but safety
        if date_end < date_start:
            date_start, date_end = date_end, date_start

        numdays = (date_end - date_start).days  # attention, the library return the next day after selection so no need for +1
        return [date_start + datetime.timedelta(days=x) for x in range(numdays)]
    return []


def set_or_update_absences(user: User, date_start: datetime.date, date_end: datetime.date, reason: str | None = None):
    date_list = __generate_list_of_dates(date_start, date_end)

    if date_list:
        absences_to_create = [Absence(user=user, date=d, reason=reason) for d in date_list]

        # ignore_conflicts=True permet de sauter les erreurs d'unicité (IntegrityError)
        Absence.objects.bulk_create(
            absences_to_create, update_conflicts=True, update_fields=["reason"], unique_fields=["user", "date"]
        )

    return len(date_list)


def remove_absences(user: User, date_start: datetime.date, date_end: datetime.date):
    date_list = __generate_list_of_dates(date_start, date_end)

    if date_list:
        Absence.objects.filter(user=user, date__in=date_list).delete()

    return len(date_list)


def get_absences(user: User, date_start: datetime.date, date_end: datetime.date):
    return Absence.objects.filter(user=user, date__gte=date_start, date__lt=date_end)
