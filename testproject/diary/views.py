from .forms import PagePutOutForm
from django.utils.dateparse import parse_datetime  # これを追加
from .forms import PageForm
from .models import Page
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from django.urls import reverse
from .forms import PageForm, ItemMstForm, BrandMstForm, HumanMstForm, QtyUnitMstForm, WtUnitMstForm, AreaMstForm, PagePutOutForm
from .models import Page, ItemMst, BrandMst, HumanMst, QtyUnitMst, WtUnitMst, AreaMst, SectionMst, PagePutOut
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
# QRcode作成
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        datetime_now = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime("%Y年%m月%d日 %H時%M分%S秒")
        return render(
            request, "diary/index.html", {"datetime_now": datetime_now})


class PageCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PageForm()
        return render(request, "diary/page_form.html", {"form": form})

    def post(self, request):
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save()  # 保存したオブジェクトを取得

            # QRコード生成ページの絶対URLを取得
            current_site = get_current_site(request)
            qr_url = f"http://{current_site.domain}{reverse('diary:qr_create', kwargs={'id': page.id})}"
            print(f"QR URL (server-side): {qr_url}")  # サーバー側でデバッグ用に確認

            # 新しいタブでQRコードを開くためのJavaScriptを埋め込む
            return render(request, "diary/redirect_with_qr.html", {"qr_url": qr_url})

        return render(request, "diary/page_form.html", {"form": form})


class PageListView(LoginRequiredMixin, View):
    def get(self, request):
        code_item = request.GET.get('code_item', '')
        item = request.GET.get('item', '')
        item_brand = request.GET.get('item_brand', '')
        area = request.GET.get('area', '')
        area_detail = request.GET.get('area_detail', '')
        put_human = request.GET.get('put_human', '')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        page_list = Page.objects.all()

        if code_item:
            page_list = page_list.filter(code_item__code__icontains=code_item)
        if item:
            page_list = page_list.filter(code_item__name__icontains=item)
        if item_brand:
            page_list = page_list.filter(
                code_item_brand__name__icontains=item_brand)
        if area:
            page_list = page_list.filter(code_area__name__icontains=area)
        if area_detail:
            page_list = page_list.filter(area_detail__icontains=area_detail)
        if put_human:
            page_list = page_list.filter(
                code_put_human__name__icontains=put_human)

        if start_date:
            page_list = page_list.filter(put_date__gte=start_date)
        if end_date:
            end_datetime = datetime.strptime(
                end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            page_list = page_list.filter(put_date__lte=end_datetime)

        context = {
            'page_list': page_list,
            'code_item': code_item,
            'item': item,
            'item_brand': item_brand,
            'area': area,
            'area_detail': area_detail,
            'put_human': put_human,
            'start_date': start_date,
            'end_date': end_date,
        }

        return render(request, "diary/page_list.html", context)


class PageDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        return render(request, "diary/page_detail.html", {"page": page})


class PageUpdateView(LoginRequiredMixin, View):
    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        form = PageForm(instance=page)
        return render(request, "diary/page_update.html", {"form": form, "page": page})

    def post(self, request, id):
        page = get_object_or_404(Page, id=id)
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            return redirect("diary:page_detail", id=id)
        return render(request, "diary/page_update.html", {"form": form, "page": page})


class PagePutOutView(LoginRequiredMixin, View):
    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        form = PageForm(instance=page)
        sections = SectionMst.objects.all()
        return render(request, "diary/page_putout.html", {"form": form, "page": page, "sections": sections})

    def post(self, request, id):
        page = get_object_or_404(Page, id=id)
        form = PageForm(request.POST, request.FILES, instance=page)
        putout_form = PagePutOutForm(request.POST)

        subtract_weight = request.POST.get('subtract_weight')
        subtract_quantity = request.POST.get('subtract_quantity')
        put_date_str = request.POST.get('put_date')

        # 日時形式を変換
        put_date = parse_datetime(put_date_str)  # parse_datetime を使って変換
        if put_date is None:
            form.add_error('put_date', 'エラー：日時形式が正しくありません。')
        else:
            page.put_date = put_date

        if subtract_quantity and subtract_quantity.strip():
            try:
                subtract_quantity = float(subtract_quantity)
                if page.put_qty - subtract_quantity <= 0:
                    form.add_error(None, "エラー：出庫数量がマイナスになります。")
            except ValueError:
                form.add_error(None, "エラー：無効な数値が入力されました。")
        else:
            form.add_error(None, "エラー：出庫数量が入力されていません。")

        if subtract_weight and subtract_weight.strip():
            try:
                subtract_weight = float(subtract_weight)
                if page.put_wt - subtract_weight <= 0:
                    form.add_error(None, "エラー：出庫重量がマイナスになります。")
            except ValueError:
                form.add_error(None, "エラー：無効な数値が入力されました。")
        else:
            form.add_error(None, "エラー：出庫重量が入力されていません。")

        if not form.errors and putout_form.is_valid():  # エラーがない場合のみリダイレクト
            page.put_wt -= subtract_weight
            page.put_qty -= subtract_quantity
            page.save()

            putout_section_code = request.POST.get('putout_section')
            putout_section = get_object_or_404(
                SectionMst, code=putout_section_code)

            PagePutOut.objects.create(
                page=page,
                code_putout_human=page.code_put_human,
                old_put_qty=page.put_qty + subtract_quantity,
                putout_qty=subtract_quantity,
                old_put_wt=page.put_wt + subtract_weight,
                putout_wt=subtract_weight,
                putout_section=putout_section
            )

            return redirect('diary:page_list')

        return render(request, "diary/page_putout.html", {"form": form, "page": page, "sections": SectionMst.objects.all()})


class PutOutListView(LoginRequiredMixin, View):
    def get(self, request):
        page_put_outs = PagePutOut.objects.all()
        code_item = request.GET.get('code_item', '')
        item = request.GET.get('item', '')
        item_brand = request.GET.get('item_brand', '')
        area = request.GET.get('area', '')
        area_detail = request.GET.get('area_detail', '')
        putout_human = request.GET.get('putout_human', '')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if code_item:
            page_put_outs = page_put_outs.filter(
                page__code_item__code__icontains=code_item)
        if item:
            page_put_outs = page_put_outs.filter(
                page__code_item__name__icontains=item)
        if item_brand:
            page_put_outs = page_put_outs.filter(
                page__code_item_brand__name__icontains=item_brand)
        if area:
            page_put_outs = page_put_outs.filter(
                page__code_area__name__icontains=area)
        if area_detail:
            page_put_outs = page_put_outs.filter(
                page__area_detail__icontains=area_detail)
        if putout_human:
            page_put_outs = page_put_outs.filter(
                code_putout_human__name__icontains=putout_human)

        if start_date:
            page_put_outs = page_put_outs.filter(putout_date__gte=start_date)
        if end_date:
            end_datetime = datetime.strptime(
                end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            page_put_outs = page_put_outs.filter(putout_date__lte=end_datetime)

        context = {
            'page_put_outs': page_put_outs,
            'code_item': code_item,
            'item': item,
            'item_brand': item_brand,
            'area': area,
            'area_detail': area_detail,
            'putout_human': putout_human,
            'start_date': start_date,
            'end_date': end_date,
        }
        return render(request, "diary/page_putoutlist.html", context)


class PageDeleteView(LoginRequiredMixin, View):
    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        return render(request, "diary/page_confirm_delete.html", {"page": page})

    def post(self, request, id):
        page = get_object_or_404(Page, id=id)
        page.delete()
        return redirect('diary:page_list')


class MasterItemView(LoginRequiredMixin, View):
    def get(self, request):
        form = ItemMstForm()
        mst = ItemMst.objects.all()
        return render(request, "diary/master_item.html", {"form": form, "mst": mst})

    def post(self, request):
        form = ItemMstForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("diary:master_item")
        return render(request, "diary/master_item.html", {"form": form})


class MasterBrandView(LoginRequiredMixin, View):
    def get(self, request):
        form = BrandMstForm()
        mst = BrandMst.objects.all()
        return render(request, "diary/master_brand.html", {"form": form, "mst": mst})

    def post(self, request):
        form = BrandMstForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("diary:master_brand")
        return render(request, "diary/master_brand.html", {"form": form})

# QRcode作成


class QrCreateView(LoginRequiredMixin, View):
    def get(self, request, id):
        # データを取得（例えばURL）
        page = get_object_or_404(Page, id=id)
        data = f"https://diary/page/{id}/update/"
        # QRコード生成
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10, border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # 画像を一時ファイルに保存
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        file_path = default_storage.save(
            f'qrcodes/{id}.png', ContentFile(buffer.read()))

        # 新しいウィンドウで画像を表示するURLにリダイレクト
        image_url = default_storage.url(file_path)

        # 必要なデータをテンプレートに渡す
        context = {
            'page': page,
            'qr_image_url': image_url
        }
        return render(request, 'diary/qr_create.html', context)


# 履歴確認


class PageHistoryView(LoginRequiredMixin, ListView):
    template_name = 'diary/page_history.html'
    context_object_name = 'history'

    def get_queryset(self):
        self.page = get_object_or_404(Page, pk=self.kwargs['pk'])
        return self.page.history.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.page
        changes = []
        history = context['history']

        for i in range(1, len(history)):
            diff = history[i].diff_against(history[i - 1])
            field_changes = []
            for change in diff.changes:
                field = self.get_field_verbose_name(Page, change.field)
                field_changes.append({
                    'field': field,
                    'old': change.old,
                    'new': change.new,
                })
            changes.append({
                'history_date': history[i].history_date,
                'history_user': history[i].history_user,
                'changes': field_changes
            })

        context['changes'] = changes
        return context

    def get_field_verbose_name(self, model, field_name):
        field = model._meta.get_field(field_name)
        return field.verbose_name if field.verbose_name else field_name


index = IndexView.as_view()
page_create = PageCreateView.as_view()
page_list = PageListView.as_view()
page_detail = PageDetailView.as_view()
page_update = PageUpdateView.as_view()
page_putout = PagePutOutView.as_view()
page_putoutlist = PutOutListView.as_view()
page_delete = PageDeleteView.as_view()
master_item = MasterItemView.as_view()
master_brand = MasterBrandView.as_view()
qr_create = QrCreateView.as_view()
