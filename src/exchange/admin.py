from django.contrib import admin
from django.utils import timezone

from exchange.models import Category, Chat, Message, CategoryProposal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = [
        "title",
        "parent",
    ]
    ordering = [
        "id",
        "parent",
    ]


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    model = Chat
    list_display = [
        "id",
        "created",
        "topic",
    ]
    ordering = [
        "-created",
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = [
        "id",
        "chat",
        "sender",
        "recipient",
        "is_read",
        "created",
    ]
    ordering = [
        "-created",
    ]


@admin.register(CategoryProposal)
class CategoryProposalAdmin(admin.ModelAdmin):
    model = CategoryProposal
    list_display = [
        "id",
        "title",
        "parent",
        "user",
        "status",
        "created",
    ]
    list_filter = ["status", "parent"]
    search_fields = ["title", "description"]
    actions = ["approve_proposals", "reject_proposals"]

    @admin.action(description="Схвалити обрані та створити категорії")
    def approve_proposals(self, request, queryset):
        created_count = 0
        updated = 0
        for proposal in queryset:
            # Create Category if not exists
            Category.objects.get_or_create(title=proposal.title, parent=proposal.parent)
            if proposal.status != CategoryProposal.Status.APPROVED:
                proposal.status = CategoryProposal.Status.APPROVED
                proposal.updated = timezone.now()
                proposal.save(update_fields=["status", "updated"])
                updated += 1
                created_count += 1
        self.message_user(request, f"Схвалено {updated} запропонованих категорій.")

    @admin.action(description="Відхилити обрані")
    def reject_proposals(self, request, queryset):
        count = 0
        for proposal in queryset.exclude(status=CategoryProposal.Status.REJECTED):
            proposal.status = CategoryProposal.Status.REJECTED
            proposal.updated = timezone.now()
            proposal.save(update_fields=["status", "updated"])
            count += 1
        self.message_user(request, f"Відхилено {count} запропонованих категорій.")
