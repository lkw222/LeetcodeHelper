from  django import forms

class CompanyForm(forms.Form):
    google = forms.BooleanField(label="Google test")
    amazon = forms.BooleanField()
    facebook = forms.BooleanField()
