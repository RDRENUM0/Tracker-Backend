from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DailyEntry, Expense, TaskDone, PhysicalActivity

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'created_at', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacje osobiste', {'fields': ('first_name', 'last_name', 'email')}),
        ('Uprawnienia', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Inline dla Expense (wydatków)
class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1
    fields = ('amount', 'description')
    classes = ('collapse',)

# Inline dla TaskDone (wykonanych zadań)
class TaskDoneInline(admin.TabularInline):
    model = TaskDone
    extra = 1
    fields = ('description',)
    classes = ('collapse',)

# Inline dla PhysicalActivity (aktywności fizycznych)
class PhysicalActivityInline(admin.TabularInline):
    model = PhysicalActivity
    extra = 1
    fields = ('activity', 'duration')
    classes = ('collapse',)

# Daily Entry Admin
@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood', 'day_rating', 'steps', 'kilometers_traveled', 'total_expenses', 'created_at')
    list_filter = ('date', 'mood', 'day_rating', 'created_at', 'user')
    search_fields = ('user__username', 'diary_entry', 'song_of_the_day', 'achievement')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('user', 'date')
        }),
        ('Samopoczucie i ocena', {
            'fields': ('mood', 'day_rating', 'diary_entry')
        }),
        ('Aktywności i statystyki', {
            'fields': (
                'song_of_the_day', 
                'kilometers_traveled', 
                'work_time', 
                'study_time', 
                'entertainment_time', 
                'steps'
            )
        }),
        ('Osiągnięcia', {
            'fields': ('achievement',)
        }),
        ('Metadane', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ExpenseInline, TaskDoneInline, PhysicalActivityInline]
    
    def total_expenses(self, obj):
        total = sum(expense.amount for expense in obj.expenses.all())
        return f"{total:.2f} zł"
    total_expenses.short_description = 'Łączne wydatki'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('expenses')

# Expense Admin
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('daily_entry', 'amount', 'description', 'get_user', 'get_date')
    list_filter = ('daily_entry__date', 'daily_entry__user')
    search_fields = ('description', 'daily_entry__user__username')
    list_editable = ('amount', 'description')
    
    def get_user(self, obj):
        return obj.daily_entry.user.username
    get_user.short_description = 'Użytkownik'
    get_user.admin_order_field = 'daily_entry__user'
    
    def get_date(self, obj):
        return obj.daily_entry.date
    get_date.short_description = 'Data'
    get_date.admin_order_field = 'daily_entry__date'

# TaskDone Admin
@admin.register(TaskDone)
class TaskDoneAdmin(admin.ModelAdmin):
    list_display = ('daily_entry', 'description', 'get_user', 'get_date')
    list_filter = ('daily_entry__date', 'daily_entry__user')
    search_fields = ('description', 'daily_entry__user__username')
    list_editable = ('description',)
    
    def get_user(self, obj):
        return obj.daily_entry.user.username
    get_user.short_description = 'Użytkownik'
    
    def get_date(self, obj):
        return obj.daily_entry.date
    get_date.short_description = 'Data'

# PhysicalActivity Admin
@admin.register(PhysicalActivity)
class PhysicalActivityAdmin(admin.ModelAdmin):
    list_display = ('daily_entry', 'activity', 'duration', 'get_user', 'get_date')
    list_filter = ('daily_entry__date', 'daily_entry__user', 'activity')
    search_fields = ('activity', 'daily_entry__user__username')
    list_editable = ('activity', 'duration')
    
    def get_user(self, obj):
        return obj.daily_entry.user.username
    get_user.short_description = 'Użytkownik'
    
    def get_date(self, obj):
        return obj.daily_entry.date
    get_date.short_description = 'Data'

# Action do masowego usuwania
def delete_selected_entries(modeladmin, request, queryset):
    queryset.delete()
delete_selected_entries.short_description = "Usuń zaznaczone wpisy"

# Dodanie akcji do DailyEntryAdmin
DailyEntryAdmin.actions = [delete_selected_entries]

# Konfiguracja strony admina
admin.site.site_header = "Daily Tracker - Panel Administracyjny"
admin.site.site_title = "Daily Tracker Admin"
admin.site.index_title = "Witaj w panelu administracyjnym Daily Tracker"