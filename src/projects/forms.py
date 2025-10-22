from django import forms


class OfferCreateForm(forms.Form):
    """Невидимая форма створеноия предложения на выполнение проєкта."""

    project_id = forms.IntegerField()


class OfferSetStatusForm(forms.Form):
    """Невидимая форма зміненоия статуса предложения на выполнение проєкта."""

    new_status = forms.CharField()
