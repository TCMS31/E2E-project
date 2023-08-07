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
            if isinstance(widget, forms.CheckboxSelectMultiple):
                # Django puts a widget-level class on the wrapping <div>, not the
                # inputs, so the checkbox list is styled from the template CSS.
                continue
            if isinstance(widget, forms.Select):
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
        # Checkboxes instead of a multi-select: no Cmd/Ctrl-click to learn, and
        # they work with a thumb on a phone.
        widgets = {'teams': forms.CheckboxSelectMultiple}
        help_texts = {'teams': 'Tick every team this player is on. Leave all blank for none.'}

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()
