from  django import forms

class Search(forms.Form):
    google = forms.BooleanField(label="Google test")
    amazon = forms.BooleanField()
    facebook = forms.BooleanField()
