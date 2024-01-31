from django.shortcuts import render, HttpResponse
from App.models import Customer, Loan
from django.db import models
from datetime import date, timedelta


# Create your views here.
def index(request):
    res = HttpResponse('<h1>Welcome, to Credit Approval System!</h1>')
    return res


def register(request):
    if request.method == 'POST':
        try: 
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            age = request.POST['age']
            phone_number = request.POST['phone_number']
            monthly_salary = int(request.POST['monthly_salary'])

            # calculating approved limit
            cal_number = 36 * monthly_salary
            # rounding off to lakhs
            def roundLakh(cal_number):
                return round(cal_number / 100000) * 100000
            # final approved limit store here
            approved_limit = roundLakh(cal_number)

            #checking lastest available id number
            max_id = Customer.objects.aggregate(models.Max('id'))['id__max']
            next_id = max_id + 1 if max_id else 1

            # creating object
            cus = Customer.objects.create(id=next_id,first_name=first_name, last_name=last_name, age=age,phone_number=phone_number, monthly_salary= monthly_salary, approved_limit=approved_limit)

            # creating response msg
            res = f"Customer ID: <b>{cus.id}</b><br>First Name: <b>{cus.first_name}</b><br>Last Name: <b>{cus.last_name}</b><br>Age: <b>{cus.age}</b><br>Phone Number: <b>{cus.phone_number}</b><br>Monthly Income: <b>Rs. {cus.monthly_salary}</b><br>Approved Limit: <b>Rs. {cus.approved_limit}</b>"

            return HttpResponse(res)
        except ValueError as e:
            return HttpResponse('Try Agian! Refresh the page.')

    return render(request, 'register.html')


def check_eligibility(request):
    customer_id = request.GET.get('customer_id')
    loan_amount = request.GET.get('loan_amount')
    interest_rate = request.GET.get('interest_rate')
    tenure = request.GET.get('tenure')

    # if inputs are not None 
    if loan_amount is not None and interest_rate is not None and tenure is not None:
        try:
            # convert string to float and int
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)

            #get customer info from database
            customer = Customer.objects.get(id=customer_id)
            #calling function from Models.py of class Loan to get credit score
            credit_score = Loan.calculate_credit_score(customer, customer_id)

            
            current_date = date.today()
            # filtering all issued Loan Info 
            cus_loan = Loan.objects.filter(customer=customer_id, end_date__gte=current_date)

            total_current_emis_amt = 0
            for loan in cus_loan:
                # total EMIs amount of a customer in a month
                total_current_emis_amt += loan.monthly_repayment
            

            if total_current_emis_amt > (customer.monthly_salary/2):
                return HttpResponse('Not Eligible')
            

            if credit_score > 50:
                # calculating EMI
                emi = loan_amount * interest_rate / 100
                emi += loan_amount
                emi /= tenure
                
                res = f"Customer ID: <b>{customer_id}</b><br>Approval: <b>{True}</b><br>Interest rate: <b>{interest_rate}</b><br>Corrected Interest Rate: <b>{interest_rate}</b><br>Tenure: <b>{tenure}</b><br>Monthly Installment: <b>Rs. {round(emi, 2)}</b>"

                return HttpResponse(res)
            elif 50 > credit_score > 30:
                emi = loan_amount * 0.12
                emi += loan_amount
                emi /= tenure

                res = f"Customer ID: <b>{customer_id}</b><br>Approval: <b>{True}</b><br>Interest rate: <b>{interest_rate}</b><br>Corrected Interest Rate: <b>12%</b><br>Tenure: <b>{tenure}</b><br>Monthly Installment: <b>Rs. {round(emi, 2)}</b>"

                return HttpResponse(res)
            elif 30 > credit_score > 10:
                emi = loan_amount * 0.16
                emi += loan_amount
                emi /= tenure

                res = f"Customer ID: <b>{customer_id}</b><br>Approval: <b>{True}</b><br>Interest rate: <b>{interest_rate}</b><br>Corrected Interest Rate: <b>16%</b><br>Tenure: <b>{tenure}</b><br>Monthly Installment: <b>Rs. {round(emi, 2)}</b>"

                return HttpResponse(res)
            elif 10 > credit_score:
                return HttpResponse('Not Eligible')
        except ValueError as e:
            return HttpResponse('Try Agian! Refresh the page.')
        except Customer.DoesNotExist:
            res = f"Customer ID {customer_id} Does Not Exist in database. Try with different ID"
            return HttpResponse(res)


    return render(request, 'check-create-loan.html')


def create_loan(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            loan_amount = request.POST.get('loan_amount')
            interest_rate = request.POST.get('interest_rate')
            tenure = request.POST.get('tenure')

            # convert string to float and int
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)

            #get customer info from database
            customer = Customer.objects.get(id=customer_id)
            #calling function from Models.py of class Loan to get credit score
            credit_score = Loan.calculate_credit_score(customer, customer_id)

            current_date = date.today()
            # filtering all issued Loan Info 
            cus_loan = Loan.objects.filter(customer=customer_id, end_date__gte=current_date)

            total_current_emis_amt = 0
            for loan in cus_loan:
                total_current_emis_amt += loan.monthly_repayment
            

            if total_current_emis_amt > (customer.monthly_salary/2):
                res = f"Loan ID: <b>None</b><br>Customer ID: <b>{customer_id}</b><br>Loan Approved: <b>{False}</b><br>Message: You are not eligible for applying loan due to Total EMIs amount is greater than your 50% of your monthly salary"

                return HttpResponse(res)
            

            if credit_score > 50:
                emi = loan_amount * interest_rate / 100
                emi += loan_amount
                emi /= tenure

                max_id = Loan.objects.aggregate(models.Max('id'))['id__max']
                next_id = max_id + 1 if max_id else 1

                new_loan = Loan.objects.create(id=next_id, customer=customer, loan_amount=loan_amount, tenure=tenure, interest_rate=interest_rate, monthly_repayment=emi, emis_paid_on_time=0, start_date=date.today(), end_date=(date.today() + timedelta(days=tenure * 30)))

                
                res = f"Loan ID: <b>{new_loan.id}</b><br>Customer ID: <b>{new_loan.customer.id}</b><br>Loan Approved: <b>{True}</b><br>Message: Loan is Approved Successfuly with Interest Rate of {interest_rate}% <br>Monthly Installment: <b>Rs. {new_loan.monthly_repayment}</b>"

                return HttpResponse(res)
            elif 50 > credit_score > 30:
                emi = loan_amount * 0.12
                emi += loan_amount
                emi /= tenure

                max_id = Loan.objects.aggregate(models.Max('id'))['id__max']
                next_id = max_id + 1 if max_id else 1

                new_loan = Loan.objects.create(id=next_id, customer=customer, loan_amount=loan_amount, tenure=tenure, interest_rate=12, monthly_repayment=emi, emis_paid_on_time=0, start_date=date.today(), end_date=(date.today() + timedelta(days=tenure * 30)))

                res = f"Loan ID: <b>{new_loan.id}</b><br>Customer ID: <b>{new_loan.customer.id}</b><br>Loan Approved: <b>{True}</b><br>Message: Loan is Approved Successfuly with Interest Rate of 12% <br>Monthly Installment: <b>Rs. {new_loan.monthly_repayment}</b>"

                return HttpResponse(res)
            elif 30 > credit_score > 10:
                emi = loan_amount * 0.16
                emi += loan_amount
                emi /= tenure

                max_id = Loan.objects.aggregate(models.Max('id'))['id__max']
                next_id = max_id + 1 if max_id else 1

                new_loan = Loan.objects.create(id=next_id, customer=customer, loan_amount=loan_amount, tenure=tenure, interest_rate=16, monthly_repayment=emi, emis_paid_on_time=0, start_date=date.today(), end_date=(date.today() + timedelta(days=tenure * 30)))

                res = f"Loan ID: <b>{new_loan.id}</b><br>Customer ID: <b>{new_loan.customer.id}</b><br>Loan Approved: <b>{True}</b><br>Message: Loan is Approved Successfuly with Interest Rate of 16% <br>Monthly Installment: <b>Rs. {new_loan.monthly_repayment}</b>"

                return HttpResponse(res)
            elif 10 > credit_score:
                res = f"Loan ID: <b>None</b><br>Customer ID: <b>{customer_id}</b><br>Loan Approved: <b>{False}</b><br>Message: You are not eligible for applying loan due to low credit score."

                return HttpResponse(res)
        except ValueError as e:
            return HttpResponse('Try Agian! Refresh the page.')
        except Customer.DoesNotExist:
            res = f"Customer ID {customer_id} Does Not Exist in database. Try with different ID"
            return HttpResponse(res)

    return render(request, 'check-create-loan.html')


def view_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id)

    # customer detail in JSON form
    cus_detail = {
        'id': loan.customer.id,
        'first name': loan.customer.first_name,
        'last name': loan.customer.last_name,
        'phone number': loan.customer.phone_number,
        'age': loan.customer.age,
    }

    res = f"Loan ID: <b>{loan.id}</b><br>Customer: <b>{cus_detail}</b><br>Loan Amount: <b>Rs. {loan.loan_amount}</b><br>Interest Rate: <b>{loan.interest_rate}%</b><br>Monthly Installment: <b>Rs. {loan.monthly_repayment}</b>"

    return HttpResponse(res)


def view_customer_loans(request, customer_id):
    cus_loans = Loan.objects.filter(customer=customer_id)
    
    # for each loan of a customer
    res = ''
    for loan in cus_loans:
        res += f"<br>Loan ID: <b>{loan.id}</b><br>"
        res += f"Loan Amount: <b>Rs. {loan.loan_amount}</b><br>"
        res += f"Interest Rate: <b>{loan.interest_rate}%</b><br>"
        res += f"Monthly Installment: <b>{loan.monthly_repayment}</b><br>"
        res += f"Repayments Left: <b>{round(loan.tenure - loan.emis_paid_on_time)}</b><br><br>"

    return HttpResponse(res)

