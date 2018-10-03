import datetime

from django import forms
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker


class MyForm(forms.Form):
    # date_field = forms.DateField(widget=DatePicker())
    # date_field_required_with_min_max_date = forms.DateField(
    #     required=True,
    #     widget=DatePicker(options={"minDate": "2009-01-20", "maxDate": "2017-01-20"}),
    # )
    # time_field = forms.TimeField(
    #     widget=TimePicker(options={"enabledHours": [9, 10, 11, 12, 13, 14, 15, 16]})
    # )
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
