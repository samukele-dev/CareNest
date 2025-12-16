from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_email_availability(request):
    """Check if email is available for registration"""
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response(
            {"error": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    exists = User.objects.filter(email__iexact=email).exists()
    
    return Response({
        "email": email,
        "available": not exists,
        "message": "Email is already registered" if exists else "Email is available"
    })