from django import forms


class CreateServiceOrderForm(forms.Form):
    """Форма размещения замовленняа на услугу."""

    service_id = forms.IntegerField()


class OrderChangeStatusForm(forms.Form):
    """Невидимая форма зміненоия статуса замовленняа."""

    new_status = forms.CharField()
