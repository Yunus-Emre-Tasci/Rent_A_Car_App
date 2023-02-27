from rest_framework import serializers  
from .models import Car,Reservation

class CarSerializer(serializers.ModelSerializer):
    is_available=serializers.BooleanField()
    class Meta:
        model=Car
        fields=(
            "id",
            "plate_number",
            "brand",
            "model",
            "year",
            "gear",
            'rent_per_day',
            "availability",
            "is_available",
        )
        
    def get_fields(self):
        fields=super().get_fields()  
        request=self.context.get("request")     
        
        if request.user and not request.user.is_staff:
            fields.pop("availability") 
            fields.pop("plate_number") 
        
        return fields   
    
class ReservationSerializer(serializers.ModelSerializer):
    total_price=serializers.SerializerMethodField() #içerisine method_name= yazılırsa buradaki method_name e göre aşağıda fonksiyon tanımlayabiliriz.
    
    class Meta:
        model=Reservation
        fields=(
            "id",
            "customer",
            "car",
            "start_date",
            "end_date",
            "total_price",
        )  
        
        validators=[  #gönderilen bütün datanın hepsini database e gelmeden kontrol ediyor.
            serializers.UniqueTogetherValidator(
                queryset=Reservation.objects.all(),
                fields=("customer","start_date","end_date"),
                message=("You already have a reservation between these dates...")
            )
        ]  
     
    def get_total_price(self,obj):
        return obj.car.rent_per_day * (obj.end_date-obj.start_date).days    