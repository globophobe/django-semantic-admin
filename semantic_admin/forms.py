from django import forms


class RangeWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class DateRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = [forms.DateInput, forms.DateInput]
        super(DateRangeWidget, self).__init__(widgets, attrs)


class TimeRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = [forms.TimeInput(), forms.TimeInput()]
        super(TimeRangeWidget, self).__init__(widgets, attrs)
