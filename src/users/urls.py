from django.urls import path

from users.views import (
    UserPublicProfileView,
    UserUpdateBalanceView,
    UserUpdateProfileView,
    OnboardingQuestionnaireView,
)
from users.views_recommendations import UserRecommendationsView

app_name = "users"
urlpatterns = [
    path("update/<int:pk>/", UserUpdateProfileView.as_view(), name="update"),
    path("balance/", UserUpdateBalanceView.as_view(), name="update_balance"),
    path("onboarding/", OnboardingQuestionnaireView.as_view(), name="onboarding"),
    path("recommendations/", UserRecommendationsView.as_view(), name="recommendations"),
    path("<str:username>/", UserPublicProfileView.as_view(), name="public_profile"),
]
