from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from .models import User

class CustomRegisterSerializer(RegisterSerializer):
    # Remove username field since we don't use it
    username = None  # This is important!
    
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    terms_accepted = serializers.BooleanField(required=True)
    
    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'user_type': self.validated_data.get('user_type', 'client'),
            'phone_number': self.validated_data.get('phone_number', ''),
            'terms_accepted': self.validated_data.get('terms_accepted', False),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        
        # Set the user fields
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.terms_accepted = self.cleaned_data['terms_accepted']
        
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'user_type',
            'profile_completed', 'verification_status',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']