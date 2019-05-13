from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TagingList(models.Model):
    taging_list_title = models.CharField(max_length=100)

    def __str__(self):
        return self.taging_list_title

class TagingData(models.Model):
    taging_data_title = models.CharField(max_length=200)
    taging_data_detail = models.TextField()
    taging_data_created = models.DateTimeField(auto_now_add=True)
    taging_Data_modified = models.DateTimeField(null=True, blank=True)
    taging_data_ann = models.TextField(blank=True)
    taging_list = models.ForeignKey(TagingList, on_delete=models.CASCADE)
    taging_file = models.FileField(null=True, blank=True)
    taging_is_taging = models.BooleanField(default=False)
    taging_modified = models.IntegerField(default=0)
    taging_is_full_tag = models.FloatField(default=0.0)

    def __str__(self):
        return self.taging_data_title

class Profile(models.Model):
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # admin을 가리기 위한 용도
    taging_count = models.IntegerField(default=0)
    document_taging_count = models.IntegerField(default=0)
    for_document_taging_count = models.IntegerField(default=0)
    for_document_taging_count_num = models.IntegerField(default=0)

class Document(models.Model):
    datafile = models.FileField(upload_to='brat/textfile')

    def __str__(self):
        return self.datafile.path

class TagingDataRate(models.Model):
    taging_data = models.ForeignKey(TagingData, on_delete=models.CASCADE)
    taging_number = models.IntegerField()
    taging_text = models.TextField(blank=True)
    taging_tag = models.CharField(max_length=50, default="")
    taging_count = models.IntegerField(default=0)
    taging_log = models.TextField(blank=True, default="")

    def __str__(self):
        return self.taging_text

class LatestTagingData(models.Model):
    latest_taging_time = models.DateTimeField(auto_now_add=True)
    latest_taging_user = models.CharField(max_length=50)
    latest_taging_number = models.IntegerField()

    def __str__(self):
        return self.latest_taging_number
