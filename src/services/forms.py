from django import forms

from services.models import Service


class ServiceCreateForm(forms.ModelForm):
    proposed_category_title = forms.CharField(
        label="Запропонувати нову категорію (за бажанням)",
        help_text="Якщо не знайшли потрібну в списку, вкажіть назву тут — ми додамо після модерації.",
        max_length=70,
        required=False,
    )

    class Meta:
        model = Service
        fields = [
            "title",
            "category",
            "image",
            "description",
            "requirements",
            "price",
            "term",
            "portfolio_url",
        ]
        labels = {
            "title": "Назва послуги",
            "category": "Категорія (найближча)",
            "image": "Обкладинка (за бажанням)",
            "description": "Що саме я роблю (опис послуги)",
            "requirements": "Що потрібно від клієнта",
            "price": "Вартість (грн)",
            "term": "",
            "portfolio_url": "Посилання на портфоліо (за бажанням)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Коротка і чітка назва послуги"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Опишіть суть послуги, підхід та очікуваний результат для клієнта"}),
            "requirements": forms.Textarea(attrs={"rows": 4, "placeholder": "Які матеріали/доступи потрібні від клієнта"}),
            "price": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "term": forms.HiddenInput(),
            "portfolio_url": forms.URLInput(attrs={"placeholder": "https://…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default hidden term to 1 day to avoid asking про "термін"
        self.fields["term"].required = False
        if not self.initial.get("term"):
            self.initial["term"] = 1

    def clean_term(self):
        term = self.cleaned_data.get("term")
        return term or 1
