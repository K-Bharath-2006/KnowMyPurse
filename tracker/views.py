from django.shortcuts import render, redirect
from .forms import UserExpenseForm
import joblib
import os

# Load ML model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'tracker', 'expense_model.pkl')
model = joblib.load(model_path)

def home(request):
    return render(request, 'tracker/home.html')

def add_expense(request):
    if request.method == 'POST':
        form = UserExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)

            # ML prediction (normalize by weekly budget)
            weekly_budget = expense.monthly_income / 4
            x_new = [[
                expense.food / weekly_budget,
                expense.travel / weekly_budget,
                expense.medical / weekly_budget,
                expense.others / weekly_budget
            ]]
            predicted_status = model.predict(x_new)[0]

            # Save predicted status in model field if you have it
            expense.predicted_status = predicted_status
            expense.save()

            # Prepare recommendations
            recommendations = {
                'food': f'Max {0.4*weekly_budget:.2f}',
                'travel': f'Max {0.3*weekly_budget:.2f}',
                'medical': f'Max {0.2*weekly_budget:.2f}',
                'others': f'Max {0.1*weekly_budget:.2f}',
            }

            # Store prediction and recommendations in session
            request.session['predicted_status'] = predicted_status
            request.session['recommendations'] = recommendations

            # Redirect to separate result page
            return redirect('result')
    else:
        form = UserExpenseForm()

    return render(request, 'tracker/add_expense.html', {'form': form})

def result(request):
    """Show predicted status and recommendations"""
    predicted_status = request.session.get('predicted_status')
    recommendations = request.session.get('recommendations')

    if not predicted_status or not recommendations:
        # If accessed directly, redirect to add expense page
        return redirect('add_expense')

    return render(request, 'tracker/result.html', {
        'status': predicted_status,
        'recommendations': recommendations
    })

