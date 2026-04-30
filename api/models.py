from django.db import models

class Tally(models.Model):
    number = models.IntegerField(unique=True)
    is_occupied = models.BooleanField(default=False) # True when a car is there

    def __str__(self):
        return f"Tally #{self.number}"

class ParkingRecord(models.Model):
    driver_name = models.CharField(max_length=200)
    congregation = models.CharField(max_length=200)
    plate_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    tally = models.OneToOneField(Tally, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    is_checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.driver_name} - {self.plate_number}"
    
class SystemSetting(models.Model):
    current_day_text = models.CharField(max_length=100, default="Friday Day 1")

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.current_day_text
    


class SystemSetting(models.Model):
    current_day_text = models.CharField(max_length=100, default="Friday Day 1")
    
    # Banner Styles
    banner_bg_color = models.CharField(max_length=7, default="#1e293b", help_text="HEX code for banner background")
    banner_text_color = models.CharField(max_length=7, default="#ffffff", help_text="HEX code for banner text")
    
    # Tally Button Styles
    tally_bg_color = models.CharField(max_length=7, default="#ffffff", help_text="Default background for tally buttons")
    tally_active_color = models.CharField(max_length=7, default="#3b82f6", help_text="Background color when a tally is selected")

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.current_day_text