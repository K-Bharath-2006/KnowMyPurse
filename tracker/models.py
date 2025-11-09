from django.db import models

class UserExpense(models.Model):
    name = models.CharField(max_length=100)
    monthly_income = models.FloatField()
    food = models.FloatField()
    travel = models.FloatField()
    medical = models.FloatField()
    others = models.FloatField()
    total_expense = models.FloatField(blank=True, null=True)
    predicted_status = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_expense = self.food + self.travel + self.medical + self.others
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
