from django.db import models

# Create your models here.
class Jfile(models.Model):
    PRIVATE_CHOICE = (
        ('PUBLIC','Public'),
        ('PRIVATE','Private')
    )

    jfile = models.FileField(upload_to='json_files/')
    upload_date = models.DateTimeField()
    privacy = models.CharField(max_length=10, choices=PRIVATE_CHOICE, default='PUBLIC')
    user = models.CharField(max_length=255)

    def __str__(self):
        return self.jfile.name
    
    class Meta:
        verbose_name_plural = 'jfiles'
        ordering =['upload_date']