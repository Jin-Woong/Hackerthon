from django.db import models


class BusGo(models.Model):
    chat_id = models.CharField(max_length=20)
    go_bus_number = models.CharField(max_length=10)
    go_station_id = models.CharField(max_length=20)
    go_route_id = models.CharField(max_length=20)
    go_station_order = models.CharField(max_length=5)
    go_region = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.id}, {self.chat_id} {self.go_bus_number} {self.go_station_id} {self.go_route_id} {self.go_station_order} {self.go_region}'


class BusOut(models.Model):
    chat_id = models.CharField(max_length=20)
    out_bus_number = models.CharField(max_length=10)
    out_station_id = models.CharField(max_length=20)
    out_route_id = models.CharField(max_length=20)
    out_station_order = models.CharField(max_length=5)
    out_region = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.id}, {self.chat_id} {self.out_bus_number} {self.out_station_id} {self.out_route_id} {self.out_station_order} {self.out_region}'


