from django import forms
from .models import Alert

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['symbol', 'alert_type', 'threshold', 'pattern_name']
        widgets = {
            'symbol' : forms.TextInput(attrs={
                                'placeholder':'e.g. AAPL',
                                'class':'form-control',
                                'style':'text-transform:uppercase',            
                        }),
            
            'alert_type':   forms.Select(attrs={'class': 'form-select'}),
            'threshold':    forms.NumberInput(attrs={
                                'placeholder': 'e.g. 185.00',
                                'class': 'form-control',
                                'step': '0.01',
                            }),
            'pattern_name': forms.TextInput(attrs={
                                'placeholder': 'e.g. Hammer',
                                'class': 'form-control',
                            }),
        }

    def clean(self):
        cleaned      = super().clean()
        atype        = cleaned.get('alert_type', '')
        threshold    = cleaned.get('threshold')
        pattern_name = cleaned.get('pattern_name', '').strip()

        needs_threshold = {'price_above', 'price_below', 'rsi_above', 'rsi_below'}

        if atype in needs_threshold and threshold is None:
            self.add_error('threshold', 'Enter a value for this alert type.')

        if atype == 'pattern' and not pattern_name:
            self.add_error('pattern_name', 'Enter the pattern name (e.g. Hammer).')

        return cleaned