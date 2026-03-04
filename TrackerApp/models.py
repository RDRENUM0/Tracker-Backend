from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dodaj related_name aby uniknąć konfliktów
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',  # ZMIENIONE
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # ZMIENIONE
        related_query_name='customuser',
    )
    
    def __str__(self):
        return self.username
    
class DailyEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()  # Data wpisu

    # 1. Wydatki - będziemy przechowywać jako JSON lub osobna tabela. Zróbmy osobny model dla wydatków.
    # 2. Samopoczucie - skala 1-6 (emotki)
    mood = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-6
    # 3. Kartka z pamiętnika
    diary_entry = models.TextField(blank=True)
    # 4. Song of the day
    song_of_the_day = models.CharField(max_length=255, blank=True)
    # 5. Tasks done - również jako JSON lub osobna tabela. Zróbmy osobny model dla zadań.
    # 6. Ilość przejechanych kilometrów
    kilometers_traveled = models.FloatField(null=True, blank=True)
    # 7. Czas spędzony na praca/nauka/rozrywka
    work_time = models.PositiveIntegerField(null=True, blank=True)  # w minutach
    study_time = models.PositiveIntegerField(null=True, blank=True)
    entertainment_time = models.PositiveIntegerField(null=True, blank=True)
    # 8. Aktywność fizyczna - osobna tabela, bo może być wiele
    # 9. Ilość kroków
    steps = models.PositiveIntegerField(null=True, blank=True)
    # 10. Osiągnięcie dnia
    achievement = models.CharField(max_length=255, blank=True)
    # 11. Overall ocena dnia (1-10)
    day_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-10

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']  # Jeden wpis na dzień per użytkownik

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# Model dla wydatków
class Expense(models.Model):
    daily_entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.amount} - {self.description}"

# Model dla zadań wykonanych
class TaskDone(models.Model):
    daily_entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name='tasks_done')
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

# Model dla aktywności fizycznej
class PhysicalActivity(models.Model):
    daily_entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name='physical_activities')
    activity = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()  # w minutach

    def __str__(self):
        return f"{self.activity} - {self.duration} min"