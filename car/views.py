# from django.shortcuts import render
from .models import Car,Reservation
from .serializers import CarSerializer,ReservationSerializer
from .permissions import IsStaffOrReadOnly

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.db.models import Q,Exists,OuterRef
from django.utils import timezone

# Create your views here.
class CarView(ModelViewSet):
    queryset=Car.objects.all()
    serializer_class=CarSerializer
    permission_classes=(IsStaffOrReadOnly,) # list de olurdu.
    
    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        else:
            queryset=super().get_queryset().filter(availability=True)
        start=self.request.query_params.get("start")
        print(start)
        end=self.request.query_params.get("end")    
        print(end)
        
        if start is not None or end is not None:
        
            # cond1=Q(start_date__lt=end) # Q ile ayrı ayrı expressionlar tanımlayabiliyoruz ama genellikle and için değil     de veya(or) için kullanılıyor ve genellikle komplez queryler için kullanılıyor.
            # cond2=Q(end_date__gt=start)   
            # not_available=Reservation.objects.filter(start_date__lt=end , end_date__gt=start).values_list("car_id",    flat=True)
            # not_available=Reservation.objects.filter(cond1 & cond2).values_list("car_id",flat=True) #buradaki flat=True     bize tek bir liste halinde dönmesini sağlıyor, olmasaydı queryset şeklinde dönecekti.
            
            # queryset=queryset.exclude(id__in=not_available)
            queryset=queryset.annotate(
                is_available=~Exists(Reservation.objects.filter(car=OuterRef("pk"),start_date__lt=end , end_date__gt=start))
            )
        
        return queryset
    
class ReservationView(ListCreateAPIView):
    queryset=Reservation.objects.all()
    serializer_class=ReservationSerializer   
    permission_classes=(IsAuthenticated,)
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer=self.request.user)
    
class ReservationDetailView(RetrieveUpdateDestroyAPIView):
    queryset=Reservation.objects.all()
    serializer_class=ReservationSerializer  
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        end=serializer.validated_data.get("end_date")
        car=serializer.validated_data.get("car")
        start=instance.start_date
        today=timezone.now().date()
        
        if Reservation.objects.filter(car=car).exists():  #exists boolean değer dönüyor, var mı yok mu diye.
            for res in Reservation.objects.filter(car=car,end_date__gte=today):
                if start < res.start_date < end:
                    return Response({"message": "Car is not available..."})
        
        return super().update(request, *args, **kwargs)        
        


        
        
