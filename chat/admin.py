from django.contrib import admin
from .models import ChatHistory, IntentLog

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'intent', 'confidence', 'created_at')
    list_filter = ('intent', 'is_helpful', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at',)

@admin.register(IntentLog)
class IntentLogAdmin(admin.ModelAdmin):
    list_display = ('text', 'predicted_intent', 'confidence', 'created_at')
    list_filter = ('predicted_intent', 'is_correct')
    search_fields = ('text',)
