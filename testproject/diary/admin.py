from django.contrib import admin
from .models import Page, PagePutOut, ItemMst, BrandMst, AreaMst, HumanMst, QtyUnitMst, WtUnitMst, SectionMst


class PageAdmin(admin.ModelAdmin):
    list_display = ('put_date', 'code_item', 'code_item_brand',
                    'put_qty', 'put_qty_unit', 'put_wt', 'put_wt_unit',
                    )


class PagePutOutAdmin(admin.ModelAdmin):
    list_display = ('putout_date', 'code_putout_human', 'old_put_qty',
                    'putout_qty', 'old_put_wt', 'putout_wt', 'putout_section',
                    'created_at', 'updated_at', 'page_id')

    def page_id(self, obj):
        return obj.page.id
    page_id.short_description = 'Page ID'


class ItemMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class BrandMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'item')


class AreaMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class HumanMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class QtyUnitMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class WtUnitMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class SectionMstAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


admin.site.register(Page, PageAdmin)
admin.site.register(PagePutOut, PagePutOutAdmin)
admin.site.register(ItemMst, ItemMstAdmin)
admin.site.register(BrandMst, BrandMstAdmin)
admin.site.register(AreaMst, AreaMstAdmin)
admin.site.register(HumanMst, HumanMstAdmin)
admin.site.register(QtyUnitMst, QtyUnitMstAdmin)
admin.site.register(WtUnitMst, WtUnitMstAdmin)
admin.site.register(SectionMst, SectionMstAdmin)
