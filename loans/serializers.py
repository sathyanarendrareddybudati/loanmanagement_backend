from rest_framework import serializers
from .models import User, Payment, Loan
from loanmanagement_backend.tasks import calculate_credit_score


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'aadhar_id', 'annual_income', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('confirm_password')
        
        if password != password2:
            raise serializers.ValidationError("Password and confirm password don't match")
        
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields=['email','password']


class LoanSerializer(serializers.ModelSerializer):
    LOAN_TYPES = (
        ('Car', 'Car'),
        ('Home', 'Home'),
        ('Education', 'Education'),
        ('Personal', 'Personal'),
    )

    loan_type = serializers.ChoiceField(choices=LOAN_TYPES)
    loan_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Loan
        fields = ['loan_type','loan_amount', 'interest_rate', 'term_period', 'disbursement_date', ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'