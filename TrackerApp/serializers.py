from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Hasła nie są identyczne."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'created_at')

from rest_framework import serializers
from .models import DailyEntry, Expense, TaskDone, PhysicalActivity

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description']

class TaskDoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDone
        fields = ['id', 'description']

class PhysicalActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalActivity
        fields = ['id', 'activity', 'duration']

class DailyEntrySerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True, required=False)
    tasks_done = TaskDoneSerializer(many=True, required=False)
    physical_activities = PhysicalActivitySerializer(many=True, required=False)

    class Meta:
        model = DailyEntry
        fields = [
            'id', 'date', 'mood', 'diary_entry', 'song_of_the_day', 
            'kilometers_traveled', 'work_time', 'study_time', 'entertainment_time',
            'steps', 'achievement', 'day_rating',
            'expenses', 'tasks_done', 'physical_activities'
        ]

    def create(self, validated_data):
        expenses_data = validated_data.pop('expenses', [])
        tasks_done_data = validated_data.pop('tasks_done', [])
        physical_activities_data = validated_data.pop('physical_activities', [])
        
        daily_entry = DailyEntry.objects.create(**validated_data)
        
        # Sprawdź czy dane istnieją przed tworzeniem
        if expenses_data:
            for expense_data in expenses_data:
                Expense.objects.create(daily_entry=daily_entry, **expense_data)
        
        if tasks_done_data:
            for task_data in tasks_done_data:
                TaskDone.objects.create(daily_entry=daily_entry, **task_data)
                
        if physical_activities_data:
            for activity_data in physical_activities_data:
                PhysicalActivity.objects.create(daily_entry=daily_entry, **activity_data)
                
        return daily_entry

    def update(self, instance, validated_data):
        # Aktualizacja DailyEntry
        instance.mood = validated_data.get('mood', instance.mood)
        instance.diary_entry = validated_data.get('diary_entry', instance.diary_entry)
        instance.song_of_the_day = validated_data.get('song_of_the_day', instance.song_of_the_day)
        instance.kilometers_traveled = validated_data.get('kilometers_traveled', instance.kilometers_traveled)
        instance.work_time = validated_data.get('work_time', instance.work_time)
        instance.study_time = validated_data.get('study_time', instance.study_time)
        instance.entertainment_time = validated_data.get('entertainment_time', instance.entertainment_time)
        instance.steps = validated_data.get('steps', instance.steps)
        instance.achievement = validated_data.get('achievement', instance.achievement)
        instance.day_rating = validated_data.get('day_rating', instance.day_rating)
        instance.save()

        # Aktualizacja powiązanych obiektów (expenses, tasks_done, physical_activities)
        # Dla uproszczenia, usuniemy stare i dodamy nowe
        instance.expenses.all().delete()
        instance.tasks_done.all().delete()
        instance.physical_activities.all().delete()

        expenses_data = validated_data.get('expenses', [])
        for expense_data in expenses_data:
            Expense.objects.create(daily_entry=instance, **expense_data)

        tasks_done_data = validated_data.get('tasks_done', [])
        for task_data in tasks_done_data:
            TaskDone.objects.create(daily_entry=instance, **task_data)

        physical_activities_data = validated_data.get('physical_activities', [])
        for activity_data in physical_activities_data:
            PhysicalActivity.objects.create(daily_entry=instance, **activity_data)

        return instance