"""
Minimal IPL Auction Models
"""
from django.db import models


class Team(models.Model):
    """IPL Team with ₹125 Crore purse"""
    name = models.CharField(max_length=100)
    purse_remaining = models.DecimalField(max_digits=15, decimal_places=2, default=1250000000)
    
    def __str__(self):
        return f"{self.name} (₹{self.purse_remaining:,.0f})"


class Player(models.Model):
    """Player available for auction"""
    name = models.CharField(max_length=100)
    is_capped = models.BooleanField(default=False)
    base_price = models.DecimalField(max_digits=15, decimal_places=2, default=10000000)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, default='active')  # active, sold
    highest_bidder = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_min_base_price(self):
        """Capped: ₹2 Crore, Uncapped: ₹30 Lakh"""
        return 20000000 if self.is_capped else 3000000
    
    def __str__(self):
        return self.name
