from rest_framework import generics, permissions, filters
from django.db.models import Count
from .models import Car
from .serializers import CarSerializer

class CarListAPIView(generics.ListAPIView):
    """
    Public API endpoint to browse and search cars with filtering and pagination.
    """
    serializer_class = CarSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['make', 'model', 'description', 'location']
    ordering_fields = ['price', 'year', 'mileage', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Car.objects.filter(is_active=True).prefetch_related('images', 'features')
        params = self.request.query_params

        make = params.get('make')
        if make:
            queryset = queryset.filter(make__iexact=make)

        model = params.get('model')
        if model:
            queryset = queryset.filter(model__icontains=model)

        min_price = params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        year = params.get('year')
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except ValueError:
                pass

        condition = params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        transmission = params.get('transmission')
        if transmission:
            queryset = queryset.filter(transmission=transmission)

        body_type = params.get('body_type')
        if body_type:
            queryset = queryset.filter(body_type=body_type)

        fuel_type = params.get('fuel_type')
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)

        location = params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        status = params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        featured = params.get('featured')
        if featured and featured.lower() in ('true', '1'):
            queryset = queryset.filter(is_featured=True)

        return queryset


class CarDetailAPIView(generics.RetrieveAPIView):
    """
    Public API endpoint to retrieve vehicle details by ID.
    """
    queryset = Car.objects.filter(is_active=True).prefetch_related('images', 'features')
    serializer_class = CarSerializer
    permission_classes = [permissions.AllowAny]
