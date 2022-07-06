from django.forms import forms


class LoadForm(forms.Form):
    stock_data_file = forms.FileField()
