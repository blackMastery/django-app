from django import forms

from django.core.exceptions import ValidationError 
from django.utils.translation import ugettext_lazy as _
import datetime 


class RenewBookForm(forms.Form):
	renewal_date = forms.DateField(help_text='Enter a date bewteen now and four weeks')

	def clean_renewal_date(self):
		data = self.cleaned_date['renewal_date']

		if data < datetime.date.today():
			raise ValidationError(_('Invalid date - renewal in past'))

		if data > datetime.date.today() + datetime.timedelta(weeks=4):
			raise ValidationError(_('Invalid date - renewal more than 4 weeks'))\

		return data




