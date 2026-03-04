from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Użytkownik został pomyślnie zarejestrowany',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Logowanie udane',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Nieprawidłowe dane logowania'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Wylogowano pomyślnie'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Błąd podczas wylogowywania'}, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DailyEntry
from .serializers import DailyEntrySerializer

class DailyEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DailyEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        date = request.query_params.get('date')
        if not date:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            daily_entry = DailyEntry.objects.get(user=request.user, date=date)
            serializer = self.get_serializer(daily_entry)
            return Response(serializer.data)
        except DailyEntry.DoesNotExist:
            return Response({'error': 'Entry not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Tutaj będziemy zwracać podsumowanie dla dashboardu
        # Na razie zwrócimy wszystkie wpisy
        entries = self.get_queryset()
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)