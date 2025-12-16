from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the signup form.
        """
        user = super().save_user(request, user, form, commit=False)
        # Add custom fields from your form
        user.user_type = form.cleaned_data.get('user_type', 'client')
        user.phone_number = form.cleaned_data.get('phone_number', '')
        user.terms_accepted = form.cleaned_data.get('terms_accepted', False)
        
        if commit:
            user.save()
        return user