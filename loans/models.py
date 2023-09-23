from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, name, aadhar_id, annual_income, password=None, confirm_password=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            aadhar_id=aadhar_id,
            annual_income=annual_income,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):

    id = models.AutoField(db_column='uid', primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    aadhar_id = models.CharField(max_length=12, unique=True, validators=[RegexValidator(regex=r'^\d{12}$', message='Aadhar ID must be 12 digits')])
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    name=models.CharField(max_length=200,null=False)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','aadhar_id']

    def __str__(self):
        return "%s - %s" % (self.uuid, self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
    
class Transaction(models.Model):

    LOAN_TYPES = (
        ('DEBIT', 'DEBIT'),
        ('CREDIT', 'CREDIT'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.amount

class Loan(models.Model):

    LOAN_TYPES = (
        ('Car', 'Car'),
        ('Home', 'Home'),
        ('Education', 'Education'),
        ('Personal', 'Personal'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.loan_type
    
    def is_fully_paid(self):
        total_paid = sum(payment.amount for payment in self.payments.all())
        return total_paid >= self.loan_amount

class EMI(models.Model):

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    emi_number = models.IntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def calculate_interest(self):
        interest_rate = self.loan.interest_rate
        return interest_rate

    def __str__(self):
        return f"EMI {self.emi_number} for Loan {self.loan.id}"


class Payment(models.Model):

    loan = models.ForeignKey(Loan, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    emi_number = models.IntegerField()
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.amount
