from django.db import models
from django.core.exceptions import ValidationError


class SpyCat(models.Model):
    name = models.CharField(max_length=255)
    years_of_experience = models.IntegerField()
    breed = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spy_cats'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.breed})"

    def has_active_mission(self):
        return self.missions.filter(complete=False).exists()


class Mission(models.Model):
    cat = models.ForeignKey(
        SpyCat, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='missions'
    )
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'missions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Mission {self.id} - {'Complete' if self.complete else 'Active'}"

    def clean(self):
        if self.cat and self.cat.has_active_mission() and not self.complete:
            existing_mission = self.cat.missions.filter(complete=False).first()
            if existing_mission and existing_mission.id != self.id:
                raise ValidationError(
                    f"Cat {self.cat.name} already has an active mission (Mission ID: {existing_mission.id})"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def check_completion(self):
        """Check if all targets are complete and mark mission as complete"""
        if self.targets.exists() and self.targets.filter(complete=False).count() == 0:
            self.complete = True
            self.save()


class Target(models.Model):
    mission = models.ForeignKey(
        Mission, 
        on_delete=models.CASCADE,
        related_name='targets'
    )
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'targets'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.country})"