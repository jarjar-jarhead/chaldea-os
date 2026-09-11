from django.db import models

class Servant(models.Model):
    collection_no = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    class_name = models.CharField(max_length=50)
    rarity = models.IntegerField(default=1)
    
    # Core Base & Max Stats
    cost = models.IntegerField(default=0)
    atk_base = models.IntegerField(default=0)
    atk_max = models.IntegerField(default=0)
    hp_base = models.IntegerField(default=0)
    hp_max = models.IntegerField(default=0)
    
    # Tactical Attributes & Alignment
    attribute = models.CharField(max_length=20, default="Earth")      
    alignment = models.CharField(max_length=50, default="Neutral")    
    deck = models.CharField(max_length=10, default="QABBB")          
    
    # Noble Phantasm Summary
    np_name = models.CharField(max_length=200, blank=True, null=True)
    np_card = models.CharField(max_length=20, default="Buster")      
    np_type = models.CharField(max_length=50, default="Anti-Unit")   
    
    # Radar Parameters (Rank letters: A, B+, EX, etc.)
    param_str = models.CharField(max_length=10, default="E")
    param_end = models.CharField(max_length=10, default="E")
    param_agi = models.CharField(max_length=10, default="E")
    param_mna = models.CharField(max_length=10, default="E")
    param_lck = models.CharField(max_length=10, default="E")
    param_np = models.CharField(max_length=10, default="E")
    
    # Visual CDN Assets
    face_url = models.URLField(max_length=500, blank=True, null=True)
    art_stage1 = models.URLField(max_length=500, blank=True, null=True)
    art_stage2 = models.URLField(max_length=500, blank=True, null=True)
    art_stage3 = models.URLField(max_length=500, blank=True, null=True)
    art_stage4 = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"[{self.collection_no}] {self.name} ({self.class_name})"

    @property
    def parameter_scores(self):
        """Converts letter grades into 0-100 values for the radar chart."""
        rank_map = {
            "EX": 90, "A++": 80, "A+": 70, "A": 60,
            "B+": 55, "B": 50, "C+": 45, "C": 40,
            "D+": 35, "D": 30, "E": 20, "?": 10
        }
        return [
            rank_map.get(self.param_str.strip().upper(), 30),
            rank_map.get(self.param_end.strip().upper(), 30),
            rank_map.get(self.param_agi.strip().upper(), 30),
            rank_map.get(self.param_mna.strip().upper(), 30),
            rank_map.get(self.param_lck.strip().upper(), 30),
            rank_map.get(self.param_np.strip().upper(), 30),
        ]