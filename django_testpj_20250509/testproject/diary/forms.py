from django import forms
from django.forms import ModelForm
from .models import Page, ItemMst, BrandMst, HumanMst, QtyUnitMst, WtUnitMst, AreaMst, PagePutOut
from datetime import datetime


class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = '__all__'

    def clean_put_wt(self):
        put_wt = self.cleaned_data.get('put_wt')
        if put_wt <= 0:  # 例えば、入庫重量が0以下であればエラーとする
            raise forms.ValidationError("入庫重量は正の数でなければなりません。")
        return put_wt

    def clean_put_date(self):
        put_date = self.cleaned_data.get('put_date')
        if isinstance(put_date, str):
            try:
                # `datetime-local`形式の文字列を正しい形式に変換
                put_date = datetime.strptime(put_date, '%Y-%m-%dT%H:%M')
            except ValueError:
                raise forms.ValidationError("エラー：日時形式が正しくありません。")
        return put_date


class ItemMstForm(ModelForm):
    class Meta:
        model = ItemMst
        fields = "__all__"


class BrandMstForm(ModelForm):
    class Meta:
        model = BrandMst
        fields = "__all__"


class HumanMstForm(ModelForm):
    class Meta:
        model = HumanMst
        fields = "__all__"


class QtyUnitMstForm(ModelForm):
    class Meta:
        model = QtyUnitMst
        fields = "__all__"


class WtUnitMstForm(ModelForm):
    class Meta:
        model = WtUnitMst
        fields = "__all__"


class AreaMstForm(ModelForm):
    class Meta:
        model = AreaMst
        fields = "__all__"


class PagePutOutForm(forms.ModelForm):
    subtract_quantity = forms.IntegerField(label='出庫数量', required=True)
    subtract_weight = forms.IntegerField(label='出庫重量', required=True)

    class Meta:
        model = PagePutOut
        fields = ['subtract_quantity', 'subtract_weight', 'putout_section']
