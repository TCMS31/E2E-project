"""Model forms for the sports app.

Widget attributes are set here rather than in the templates so that the form
markup stays declarative and every input picks up the same styling.
"""

from django import forms

from .models import Player, Team


class BootstrapModelForm(forms.ModelForm):
    """Applies Bootstrap classes to every widget on the form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            else:
                widget.attrs.setdefault('class', 'form-control')


class TeamForm(BootstrapModelForm):
    class Meta:
        model = Team
        fields = ('city', 'mascot')

    def clean_city(self):
        return self.cleaned_data['city'].strip()

    def clean_mascot(self):
        return self.cleaned_data['mascot'].strip()


class PlayerForm(BootstrapModelForm):
    class Meta:
        model = Player
        fields = ('first_name', 'last_name', 'teams')
        help_texts = {'teams': 'Hold Cmd/Ctrl to select more than one team.'}

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()
