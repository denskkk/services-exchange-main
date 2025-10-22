from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from services.models import Service
from users.models import CustomUser
from users.models import DetailedQuestionnaire
from exchange.models import Category


def service_list(
    category_id: int | None = None,
    provider_id: int | None = None,
    search: str | None = None,
) -> QuerySet:
    queryset = Service.objects.select_related(
        "category", "category__parent", "category__parent__parent", "provider"
    )

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if provider_id:
        queryset = queryset.filter(provider_id=provider_id)

    if search:
        search_vector = SearchVector(
            "title", weight="A", config="russian"
        ) + SearchVector("description", weight="B", config="russian")
        search_query = SearchQuery(search, config="russian")
        queryset = (
            queryset.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query)
            )
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

    return queryset.all()


def service_get_by_id(service_id: int) -> Service | None:
    return (
        Service.objects.filter(id=service_id)
        .select_related("category__parent__parent")
        .select_related("provider")
        .first()
    )


def services_recommended_for_user(user: CustomUser, limit: int = 12) -> QuerySet:
    """
    Very simple rule-based recommendations based on user's questionnaire:
    - has_children -> suggest nanny/child-related services
    - has_pets -> pet care
    - home_type apartment/house -> cleaning/repair
    - car_owner -> car services
    - prefer_online_services -> prioritize categories often done online (design, dev, copywriting)
    Fallback: recent/active services.
    """
    qs = Service.objects.select_related("category", "provider").filter(is_active=True)
    dq: DetailedQuestionnaire | None = getattr(user, "questionnaire", None)

    category_ids: list[int] = []

    title_map = [
        (user.has_children, ["няня", "дит", "репетитор"]),
        (user.has_pets, ["твар", "кіт", "собак", "догляд за твар", "вет"]),
        (user.home_type in {"apartment", "house"}, ["прибиран", "ремонт", "сантех", "електрик"]),
        (user.car_owner, ["авто", "шиномонтаж", "діагност", "заміна масла"]),
        (user.prefer_online_services, ["дизайн", "розроб", "маркет", "копірай", "переклад"]),
    ]

    # Use detailed questionnaire to enhance keyword matching
    if dq:
        if dq.interested_children or dq.household_children > 0 or dq.has_infants:
            title_map.append((True, ["няня", "репетитор", "садок", "догляд за дітьми"]))
        if dq.interested_pets or dq.pets_cats or dq.pets_dogs or dq.pets_other:
            title_map.append((True, ["вигул", "догляд за твар", "грумінг"]))
        if dq.interested_home or dq.dwelling_type in {"apartment", "house"}:
            title_map.append((True, ["прибиран", "миття вікон", "ремонт", "сантех", "електрик"]))
        if dq.interested_auto or dq.car_owner:
            title_map.append((True, ["СТО", "шиномонтаж", "діагност", "евакуатор"]))
        if dq.interested_it:
            title_map.append((True, ["сайт", "дизайн", "розроб", "SEO", "SMM"]))
        if dq.interested_marketing:
            title_map.append((True, ["маркет", "таргет", "SMM", "контент"]))
        if dq.interested_translation:
            title_map.append((True, ["переклад", "локалізація"]))
        if dq.interested_admin:
            title_map.append((True, ["адміністрат", "підтримка", "віртуальний асистент"]))

    matched_ids: set[int] = set()
    for cond, keywords in title_map:
        if cond:
            for kw in keywords:
                ids = qs.filter(title__icontains=kw).values_list("id", flat=True)[:limit]
                matched_ids.update(ids)

    if matched_ids:
        qs = qs.filter(id__in=list(matched_ids))

    # Budget filtering if provided
    if dq and (dq.budget_min or dq.budget_max):
        if dq.budget_min:
            qs = qs.filter(price__gte=dq.budget_min)
        if dq.budget_max and dq.budget_max > 0:
            qs = qs.filter(price__lte=dq.budget_max)

    # Prefer online tilt
    if dq and dq.prefer_online:
        qs = qs.order_by(
            # prioritize titles that likely relate to online-friendly categories
            "-is_active"
        )

    # If nothing matched, try categories by heuristic names
    cat_title_keywords = [
        (user.prefer_online_services, ["Дизайн", "Разработка", "Маркетинг", "Тексты", "Переклад"]) ,
    ]
    selected_categories = Category.objects.none()
    for cond, kws in cat_title_keywords:
        if cond:
            for kw in kws:
                selected_categories = selected_categories | Category.objects.filter(title__icontains=kw)

    if selected_categories.exists():
        return qs.filter(category__in=selected_categories)[:limit]

    # Final fallback: newest active services
    return qs.order_by("-created")[:limit]


def services_latest(limit: int = 8) -> QuerySet:
    """Latest active services with related data."""
    return (
        Service.objects.filter(is_active=True)
        .select_related("category", "provider")
        .order_by("-created")[:limit]
    )
