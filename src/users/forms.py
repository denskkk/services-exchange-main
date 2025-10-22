from django import forms
from users.models import CustomUser
from users.models import DetailedQuestionnaire


class UpdateUserBalanceForm(forms.Form):
    """Форма для пополнения баланса пользователя."""

    amount = forms.IntegerField(
        label="Сума для поповнення",
        help_text="Сума в грн, яку ви хочете перевести з картки на баланс",
        min_value=100,
    )
    card_number = forms.IntegerField(
        label="Номер картки",
        help_text="Укажите номер банковской карты, с которой вы хотите пополнить баланс",
    )


class OnboardingQuestionnaireForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "has_children",
            "has_pets",
            "home_type",
            "car_owner",
            "employment_status",
            "prefer_online_services",
        ]
        widgets = {
            "has_children": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "has_pets": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "home_type": forms.Select(attrs={"class": "form-select"}),
            "car_owner": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "employment_status": forms.Select(attrs={"class": "form-select"}),
            "prefer_online_services": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class DetailedQuestionnaireForm(forms.ModelForm):
    class Meta:
        model = DetailedQuestionnaire
        exclude = ["user", "created", "updated"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Опишіть особливі побажання або деталі"}),
            "language_other": forms.TextInput(attrs={"placeholder": "Напр., польська"}),
        }
