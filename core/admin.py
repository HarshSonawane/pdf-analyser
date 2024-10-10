from django.contrib import admin
from .models import ReviewRequest, PageResult


class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ('status', 'reviewer', 'document', 'comments', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('status', 'reviewer', 'document', 'comments')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(ReviewRequest, ReviewRequestAdmin)


class PageResultAdmin(admin.ModelAdmin):
    list_display = ('review_request', 'page_number', 'service', 'flaged', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('document', 'page_number', 'service')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(PageResult, PageResultAdmin)
