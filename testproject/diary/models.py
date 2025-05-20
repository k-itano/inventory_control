from django.db import models
from pathlib import Path
from datetime import datetime
import uuid
from simple_history.models import HistoricalRecords


class ItemMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="品目コード")
    name = models.CharField(blank=False, null=False,
                            max_length=50, verbose_name="品目名称")

    def __str__(self):
        return self.name


class BrandMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="品種コード")
    name = models.CharField(blank=False, null=False,
                            max_length=50, verbose_name="品種名称")
    item = models.ForeignKey(
        ItemMst, on_delete=models.PROTECT, to_field='code', verbose_name="品目コード"
    )

    def __str__(self):
        return self.name


class AreaMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="産地コード")
    name = models.CharField(blank=False, null=False,
                            max_length=20, verbose_name="産地名称")

    def __str__(self):
        return self.name


class HumanMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="担当者コード")
    name = models.CharField(blank=False, null=False,
                            max_length=20, verbose_name="担当者名称")

    def __str__(self):
        return self.name


class QtyUnitMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="数量単位コード")
    name = models.CharField(blank=False, null=False,
                            max_length=10, verbose_name="数量単位名称")

    def __str__(self):
        return self.name


class WtUnitMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="重量単位コード")
    name = models.CharField(blank=False, null=False,
                            max_length=10, verbose_name="重量単位名称")

    def __str__(self):
        return self.name


class SectionMst(models.Model):
    code = models.IntegerField(
        blank=False, null=False, unique=True, verbose_name="部署コード")
    name = models.CharField(blank=False, null=False,
                            max_length=20, verbose_name="部署名称")

    def __str__(self):
        return self.name


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name="ID")
    code_item = models.ForeignKey(
        ItemMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="品目",
    )
    code_item_brand = models.ForeignKey(
        BrandMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="品種",
        default=0
    )
    code_area = models.ForeignKey(
        AreaMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="産地",
    )
    code_put_human = models.ForeignKey(
        HumanMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="担当者",
    )
    area_detail = models.CharField(
        blank=True, null=False, max_length=20, verbose_name="地名")
    put_date = models.DateTimeField(
        blank=False, null=False, default=datetime.now, verbose_name="入庫日時")
    put_qty = models.IntegerField(blank=False, null=False, verbose_name="入庫数")
    put_qty_unit = models.ForeignKey(
        QtyUnitMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="数量単位"
    )
    put_wt = models.IntegerField(blank=False, null=False, verbose_name="入庫重量")
    put_wt_unit = models.ForeignKey(
        WtUnitMst, on_delete=models.PROTECT, to_field='code', blank=False, null=False, verbose_name="重量単位"
    )
    picture = models.ImageField(
        upload_to="diary/picture/", blank=True, null=True, verbose_name="画像")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.code_item)

    def delete(self, *args, **kwargs):
        picture = self.picture
        super().delete(*args, **kwargs)
        if picture:
            Path(picture.path).unlink(missing_ok=True)


class PagePutOut(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    code_putout_human = models.ForeignKey(
        HumanMst, on_delete=models.PROTECT, to_field='code', verbose_name="出庫担当者"
    )
    putout_date = models.DateTimeField(auto_now_add=True, verbose_name="出庫日時")
    old_put_qty = models.IntegerField(verbose_name="以前の在庫数")
    putout_qty = models.IntegerField(verbose_name="出庫数")
    old_put_wt = models.IntegerField(verbose_name="以前の在庫重量")
    putout_wt = models.IntegerField(verbose_name="出庫重量")
    putout_section = models.ForeignKey(
        SectionMst, on_delete=models.PROTECT, to_field='code', verbose_name="出庫部署"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.page} - {self.putout_date}"
