import json
import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ads.models import Category, Ad, Location, Selection
from ads.serializers import LocationSerializer, AdSerializer, AdDetailSerializer, SelectionCreateSerializer, \
    SelectionSerializer, SelectionDetailsSerializer
from ads.permissions import AdUpdateDeletePermission, SelectionPermission


def index(request):
    return JsonResponse({'status': 'ok'}, status=200)


class CategoryListView(ListView):
    model = Category
    ordering = 'name'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        search_text = request.GET.get('name', None)
        if search_text:
            self.object_list = self.object_list.filter(name=search_text)

        total = self.object_list.count()
        page = request.GET.get('page')
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_obj = paginator.get_page(page)

        items = []
        for item in page_obj:
            items.append({
                'id': item.id,
                'name': item.name,
            })

        response = {
            'total': total,
            'items': items,
            'num_pages': math.ceil(float(total) / settings.TOTAL_ON_PAGE)
        }

        return JsonResponse(response, safe=False)


class CategoryDetailView(DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except self.model.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        cat = Category.objects.create(
            name=data['name'],
        )

        return JsonResponse({
            'id': cat.id,
            'name': cat.name,
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data = json.loads(request.body)
        self.object.name = data['name'] if data.get('name') else self.object.name

        try:
            self.object.full_clean()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=422)
        self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
        }, status=202)

    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({'status': 'ok'}, status=200)


class AdListView(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

    def get(self, request, *args, **kwargs):
        category_id = request.GET.get("cat", None)
        text = request.GET.get("text", None)
        location = request.GET.get("location", None)
        price_from = request.GET.get("price_from", None)
        price_to = request.GET.get("price_to", None)

        if category_id:
            self.queryset = self.queryset.filter(
                category_id__exact=category_id
            )
        if text:
            self.queryset = self.queryset.filter(
                name__icontains=text
            )
        if location:
            self.queryset = self.queryset.filter(
                author__locations__name__icontains=location
            )
        if price_from and price_to:
            self.queryset = self.queryset.filter(
                Q(price__gte=price_from) & Q(price__lte=price_to)
            )
        return super().get(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class AdCreateView(CreateView):
    model = Ad
    fields = ['name', 'author', 'price', 'description', 'is_published', 'category']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        ad = Ad.objects.create(
            name=data['name'],
            author_id=data['author_id'],
            price=data['price'],
            description=data['description'],
            category_id=data['category_id'],
            is_published=data['is_published']
        )

        return JsonResponse({
            'id': ad.id,
            'name': ad.name,
            'author_id': ad.author.id,
            'price': ad.price,
            'description': ad.description,
            'category_id': ad.category.id,
            'is_published': ad.is_published,
            'image': ad.image.url if ad.image else None
        }, status=201)


class AdDetailView(UpdateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDetailSerializer
    permission_classes = [IsAuthenticated]


class AdUpdateView(DestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDetailSerializer
    permission_classes = [AdUpdateDeletePermission]


@method_decorator(csrf_exempt, name='dispatch')
class AdUploadImageView(UpdateView):
    model = Ad
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.FILES.get('image'):
            self.object.image = request.FILES['image']
            self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
            'author_id': self.object.author.id,
            'price': self.object.price,
            'description': self.object.description,
            'category_id': self.object.category.id,
            'is_published': self.object.is_published,
            'image': self.object.image.url if self.object.image else None
        }, status=202)

    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class AdDeleteView(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdDetailSerializer
    permission_classes = [AdUpdateDeletePermission]


class LocationViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Location.objects.all()
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = Location.objects.all()
        location = get_object_or_404(queryset, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        queryset = Location.objects.all()
        location = get_object_or_404(queryset, pk=kwargs.get('pk'))
        serializer = LocationSerializer(location, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        queryset = Location.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = Selection.objects.all()
    permission_classes = [SelectionPermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SelectionCreateSerializer
        if self.action == 'retrieve':
            return SelectionDetailsSerializer
        return SelectionSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
