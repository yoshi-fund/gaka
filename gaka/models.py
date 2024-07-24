from django.db import models
from PIL import Image
import numpy as np

class Gaka(models.Model):
    
    class Meta:
        db_table = 'gaka'
    
    GENDER = (
        (1, '男性'),
        (2, '女性')
    )
    
    gaka_name = models.CharField('画家名', max_length=200)
    gender = models.IntegerField('性別', choices=GENDER)
    date_of_birth = models.DateField('生年月日')
    nationality = models.CharField('国籍', max_length=100)
    
    def __str__(self):
        return self.gaka_name

class Artwork(models.Model):
    
    class Meta:
        db_table = 'artworks'
    
    title_name = models.CharField('作品名', max_length=200)
    gaka = models.ForeignKey(Gaka, on_delete=models.CASCADE, related_name='artworks')
    year_of_creation = models.DateField('制作年', null=True, blank=True)
    techniques_used = models.CharField('使用技法', max_length=200, null=True, blank=True)
    
    image = models.ImageField(upload_to='artworks/')
    average_r = models.FloatField('平均R', editable=False, null=True)
    average_g = models.FloatField('平均G', editable=False, null=True)
    average_b = models.FloatField('平均B', editable=False, null=True)
    brightness = models.FloatField('明度', editable=False, null=True)
    saturation = models.FloatField('彩度', editable=False, null=True)
    emotion = models.CharField('感情', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # 一時的にコミットせずに保存して、ファイルパスを取得
        super(Artwork, self).save(*args, **kwargs)
        self.calculate_average_rgb_and_metrics()
        # 再度保存してRGB値と計算された値を更新
        super(Artwork, self).save(*args, **kwargs)
    
    def calculate_average_rgb_and_metrics(self):
        if self.image and self.image.path:
            with Image.open(self.image.path) as img:
                img = img.convert('RGB')
                np_img = np.array(img)
                avg_rgb = np.mean(np_img, axis=(0, 1))
                self.average_r = avg_rgb[0]
                self.average_g = avg_rgb[1]
                self.average_b = avg_rgb[2]
                self.brightness = self.calculate_brightness(self.average_r, self.average_g, self.average_b)
                self.saturation = self.calculate_saturation(self.average_r, self.average_g, self.average_b)
    
    def calculate_brightness(self, r, g, b):
        return max(r, g, b) / 255 * 100

    def calculate_saturation(self, r, g, b):
        max_val = max(r, g, b) / 255
        min_val = min(r, g, b) / 255
        if max_val == 0:
            return 0
        else:
            return (max_val - min_val) / max_val * 100
    
    def __str__(self):
        return f'{self.id} - {self.title_name}'
