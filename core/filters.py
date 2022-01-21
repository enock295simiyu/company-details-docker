from django_filters import FilterSet
from django_filters.filters import RangeFilter

from core.models import CompanySource
from .forms import PeopleFilterFormHelper
from .widgets import CustomRangeWidget


class AllRangeFilter(RangeFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            values = [p.organization_revenue_in_thousands_int for p in CompanySource.objects.all() if
                      p.organization_revenue_in_thousands_int is not None]

            min_value = min(values)
            max_value = max(values)
        except:
            min_value = 0
            max_value = 0
        self.extra['widget'] = CustomRangeWidget(attrs={'data-range_min': min_value, 'data-range_max': max_value})


class PeopleFilter(FilterSet):
    organization_revenue_in_thousands_int = AllRangeFilter()

    class Meta:
        model = CompanySource
        fields = ['organization_revenue_in_thousands_int']
        form = PeopleFilterFormHelper
