from django import forms
from web.models import  Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = '__all__'

