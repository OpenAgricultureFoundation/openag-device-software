import datetime

from django import forms
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker


class DateTimeForm(forms.Form):
    start_time = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                "minDate": (
                    datetime.date.today() + datetime.timedelta(minutes=2)
                ).strftime(
                    "%Y-%m-%d"
                ),  # Must be a minute from now
                "useCurrent": True,
                "collapse": False,
            },
            attrs={"placeholder": "Optional. Click to Add", "size": 20},
        )
    )
