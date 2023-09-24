from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Loan, Payment, EMI
from .serializers import UserRegistrationSerializer, UserLoginSerializer, LoanSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from loanmanagement_backend.tasks import calculate_credit_score
from decimal import Decimal



class UserRegistrationAPI(APIView):

    """
    End-Point: /api/register-user/
    """

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            user = serializer.save()
            annual_income = serializer.validated_data.get('annual_income')

            calculate_credit_score.delay(annual_income, user.id)

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginAPI(APIView):

    """
		End-Point : /api/login-user/
	"""

    def post(self, request, format=None):

        serializer=UserLoginSerializer(data=request.data)
        if serializer.is_valid():

            email=serializer.data.get('email')
            password=serializer.data.get('password')
            user=authenticate(email=email,password=password)
 
            annual_income = user.annual_income

            #updating the credit score 
            calculate_credit_score.delay(annual_income, user.id)
            
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({ 'token': token.key, 'msg': 'Login Successful' },status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':['Email or Password is not valid']}},status = status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class LoanAPI(APIView):

    """
    End-Point: /api/apply-loan/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = LoanSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            annual_income = user.annual_income
            credit_score = user.credit_score

            if credit_score >= 450 and annual_income >= 150000:
                loan_type = serializer.validated_data['loan_type']
                loan_amount = serializer.validated_data['loan_amount']
                disbursement_date = serializer.validated_data['disbursement_date']
                interest_rate = Decimal(serializer.validated_data['interest_rate'])
                tenure_months = serializer.validated_data['term_period']

                loan_bounds = {
                    'Car': 750000,
                    'Home': 8500000,
                    'Education': 5000000,
                    'Personal': 1000000,
                }

                if loan_type not in loan_bounds:
                    return Response({'error': 'Invalid loan type'}, status=status.HTTP_400_BAD_REQUEST)

                if loan_amount <= loan_bounds[loan_type]:
                    emi = loan_amount * interest_rate / Decimal('12') * (Decimal('1') + interest_rate / Decimal('12')) ** tenure_months
                    emi /= ((Decimal('1') + interest_rate / Decimal('12')) ** tenure_months - Decimal('1'))

                    monthly_income = annual_income / Decimal('12')
    
                    if emi <= Decimal('0.6') * monthly_income:
                        total_interest = (emi * tenure_months) - loan_amount

                        if total_interest > Decimal(10000):

                            loan = Loan.objects.create(
                                user=user,
                                loan_type=loan_type,
                                loan_amount=loan_amount,
                                interest_rate=interest_rate,
                                term_period=tenure_months,
                                disbursement_date=disbursement_date,
                                is_approved = True
                            )

                            emi_start_date = disbursement_date + timedelta(days=30)
                            for emi_number in range(1, tenure_months + 1):
                                emi_due_date = emi_start_date + timedelta(days=30 * emi_number)
                                EMI.objects.create(
                                    loan=loan,
                                    emi_number=emi_number,
                                    due_date=emi_due_date,
                                    amount_due=emi
                                )

                            return Response({'msg': 'Loan application submitted successfully'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'error': 'Total interest earned is too low'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'error': 'EMI exceeds 60% of monthly income'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Loan amount exceeds the allowed limit'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'User is not eligible for a loan'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class PaymentAPI(APIView):

    """
    End-Point: /api/make-payment/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            loan_id = serializer.validated_data['loan'].id
            amount = serializer.validated_data['amount']
            emi_number = serializer.validated_data['emi_number']
            emi_amount = serializer.validated_data['emi_amount']
            payment_date = serializer.validated_data.get('payment_date', datetime.now().date())

            try:
                loan = Loan.objects.get(id=loan_id)

                if loan.is_fully_paid():
                    return Response({'error': 'Loan has already been fully paid'}, status=status.HTTP_400_BAD_REQUEST)

                existing_payment = Payment.objects.filter(loan=loan, payment_date=payment_date).first()
                if existing_payment:
                    return Response({'error': 'Payment for this date already exists'}, status=status.HTTP_400_BAD_REQUEST)

                emi = EMI.objects.filter(loan=loan, emi_number=emi_number).first()
                if not emi:
                    return Response({'error': 'EMI not found for the provided loan and EMI number'}, status=status.HTTP_400_BAD_REQUEST)

                if payment_date > emi.due_date:
                    return Response({'error': 'Payment for overdue EMI is not allowed'}, status=status.HTTP_400_BAD_REQUEST)

                remaining_emi_amount = emi.amount_due - emi_amount

                if remaining_emi_amount < 0:
                    return Response({'error': 'Amount paid exceeds the EMI amount'}, status=status.HTTP_400_BAD_REQUEST)

                payment = Payment.objects.create(
                    loan=loan,
                    amount=amount,
                    payment_date=payment_date,
                    emi_number=emi_number,
                    emi_amount=emi_amount
                )

                emi.amount_due = remaining_emi_amount
                emi.is_paid = True if remaining_emi_amount == 0 else False
                emi.save()

                return Response({'msg': 'Payment registered successfully'}, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({'error': 'Loan not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetStatementAPI(APIView):

    """
    End-Point: /api/get-statement/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        loan_id = request.query_params.get('loan_id')

        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan does not exist or is closed.'}, status=status.HTTP_400_BAD_REQUEST)

        if not loan.is_fully_paid():
            past_transactions = []
            upcoming_transactions = []

            emis = EMI.objects.filter(loan=loan).order_by('due_date')

            for emi in emis:
                if emi.is_paid:
                    statement = {
                        'date': emi.due_date,
                        'principal_due': emi.amount_due - emi.calculate_interest(),
                        'interest_on_principal': emi.calculate_interest(),
                        'repayment_of_principal': emi.amount_due,
                    }
                    past_transactions.append(statement)
                else:
                    upcoming_emi = {
                        'date': emi.due_date,
                        'amount_due': emi.amount_due,
                    }
                    upcoming_transactions.append(upcoming_emi)

            response_data = {
                'past_transactions': past_transactions,
                'upcoming_transactions': upcoming_transactions,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Loan does not exist or is closed.'}, status=status.HTTP_400_BAD_REQUEST)