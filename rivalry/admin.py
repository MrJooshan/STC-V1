from django.contrib import admin
from .models import RivalryMatch, RivalryQuestion


@admin.register(RivalryMatch)
class RivalryMatchAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'status', 'winner', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('player1__phone_number', 'player2__phone_number')


@admin.register(RivalryQuestion)
class RivalryQuestionAdmin(admin.ModelAdmin):
    list_display = ('match', 'question', 'order', 'answered_by', 'is_correct')
    list_filter = ('is_correct',)
