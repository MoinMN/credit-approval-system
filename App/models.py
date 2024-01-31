from django.db import models
from datetime import date

# Create your models here.
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    monthly_salary = models.DecimalField(max_digits=100, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name} -> {self.id}"

class Loan(models.Model):
    # foreign key for customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=100, decimal_places=2)
    tenure = models.DecimalField(max_digits=100, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=10, decimal_places=1)
    monthly_repayment = models.DecimalField(max_digits=100, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    
    def calculate_credit_score(self, customer):
        credit_score = 0
        current_date = date.today()
        current_year = date.today().year

        past_loans = Loan.objects.filter(customer=customer)

        past_loans_paid_on_time = sum(loan.emis_paid_on_time for loan in past_loans)
        if past_loans_paid_on_time >= 100:
            credit_score += 25
        elif past_loans_paid_on_time >= 75:
            credit_score += 20
        elif past_loans_paid_on_time >= 50:
            credit_score += 15
        elif past_loans_paid_on_time >= 25:
            credit_score += 10
        elif past_loans_paid_on_time >= 10:
            credit_score += 5
        else:
            credit_score += 0

        num_loans_taken_in_past = past_loans.count()
        count = 0
        for loan in past_loans:
            if loan.end_date < current_date:
                count += 1

        if num_loans_taken_in_past == count:
            credit_score += 25
        elif (num_loans_taken_in_past - count) > 10:
            credit_score += 5
        elif (num_loans_taken_in_past - count) > 5:
            credit_score += 10
        elif (num_loans_taken_in_past - count) >= 1:
            credit_score += 15
        else:
            credit_score += 0

        loan_activity_current_year = past_loans.filter(customer=customer ,end_date__year__gte = current_year).count()

        if loan_activity_current_year > 10:
            credit_score += 5
        elif loan_activity_current_year > 5:
            credit_score += 15
        elif loan_activity_current_year >= 1:
            credit_score += 20
        else:
            credit_score += 0

        loan_approved_volume = sum(loan.loan_amount for loan in past_loans)

        current_loans = Loan.objects.filter(customer=customer, end_date__year__gte=current_year)
        current_loans_sum = sum(loan.loan_amount for loan in current_loans)
        
        if (loan_approved_volume - current_loans_sum) < self.approved_limit:
            credit_score += 15

        if current_loans_sum > self.approved_limit:
            credit_score = 0

        return max(0, credit_score)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name} [{self.id}]"