from django import forms
from .models import SampleSource


class SelectionForm(forms.Form):
    names = SampleSource.objects.all()
    print('helo')
    print(names)
    options = []
    for n in names:
        options.append((n.name,n.name))

    selected = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=options)
