from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count, Q, QuerySet
from orders.models import Order
from users.models import CustomUser

from projects.models import Offer, Project


def project_list(
    category_id: int | None = None,
    customer_id: int | None = None,
    exclude_with_orders: bool = False,
    search: str | None = None,
) -> QuerySet:
    queryset = Project.objects.select_related(
        "category", "category__parent", "category__parent__parent", "customer"
    ).annotate(
        offer_count=Count(
            "offers",
            filter=Q(offers__is_cancelled=False) & ~Q(offers__status="accepted"),
        )
    )

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if customer_id:
        queryset = queryset.filter(customer_id=customer_id)

    if exclude_with_orders:
        # Выбираем все заказы на проекты
        orders = Order.objects.filter(
            item_ct=ContentType.objects.get_for_model(Project)
        ).all()
        # Выбираем в список id всех проектов в этих заказов
        projects_with_orders_pks = list(orders.values_list("item_id", flat=True))
        # Исключаем проекты с id в списке
        queryset = queryset.exclude(id__in=projects_with_orders_pks)

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


def project_get_by_id(project_id: int) -> Project | None:
    return (
        Project.objects.filter(id=project_id)
        .select_related("category__parent__parent", "customer")
        .prefetch_related("offers", "offers__candidate")
        .first()
    )


def offer_list(project_id: int, candidate: CustomUser | None = None) -> QuerySet:
    queryset = Offer.objects.filter(project_id=project_id)

    if candidate:
        queryset = queryset.filter(candidate=candidate)

    return queryset.all()


def offer_get_by_id(offer_id: int) -> Offer | None:
    return (
        Offer.objects.filter(id=offer_id)
        .select_related("project", "candidate", "project__customer")
        .first()
    )
