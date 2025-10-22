from django import forms
from exchange.models import Category, CategoryProposal


class MessageCreateForm(forms.Form):
    """Форма створеноия повідомлення."""

    topic_ct = forms.CharField()
    topic_id = forms.IntegerField()
    recipient_id = forms.IntegerField()
    text = forms.CharField()
    # TODO: implement file field
    # file = forms.FileField()


class CategoryProposalForm(forms.ModelForm):
    """Форма пропозиції нової категорії.

    Пояснення: користувач може запропонувати нову категорію, якщо не знайшов потрібної.
    Запит потрапляє на модерацію адміністратору.
    """

    class Meta:
        model = CategoryProposal
        fields = ["title", "parent", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full", "placeholder": "Назва категорії"}),
            "parent": forms.Select(attrs={"class": "w-full"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "w-full", "placeholder": "Коротко опишіть, чому потрібна ця категорія"}),
        }
