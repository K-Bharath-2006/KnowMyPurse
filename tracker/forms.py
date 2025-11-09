from django import forms
from .models import UserExpense

class UserExpenseForm(forms.ModelForm):
    class Meta:
        model = UserExpense
        fields = ['name', 'monthly_income', 'food', 'travel', 'medical', 'others']
