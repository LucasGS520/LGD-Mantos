from datetime import date as _today_date
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from services.api_client import ApiError, ConnectionApiError
from storage.cache import LocalCache
from storage.offline_queue import OfflineQueue

_CACHE_KEY = "products"
_CACHE_TTL = 120
_VALID_MOV_TYPES = {"entrada", "saida", "ajuste", "devolucao"}


def _req(value: str, field: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError(f"Campo obrigatorio: {field}")
    return v


def _num(value: str, field: str, cast=float):
    v = value.strip()
    if not v:
        raise ValueError(f"Campo obrigatorio: {field}")
    try:
        return cast(v)
    except ValueError:
        raise ValueError(f"{field} deve ser um numero valido.")


class OperationalScreen(BoxLayout):
    def __init__(self, api, queue: OfflineQueue, **kwargs):
        super().__init__(orientation="vertical", padding=8, spacing=4, **kwargs)
        self.api = api
        self.cache = LocalCache()
        self.queue = queue

        # Shared list containers
        self.products_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.products_box.bind(minimum_height=self.products_box.setter("height"))
        self.suppliers_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.suppliers_box.bind(minimum_height=self.suppliers_box.setter("height"))
        self.purchases_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.purchases_box.bind(minimum_height=self.purchases_box.setter("height"))
        self.expenses_box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.expenses_box.bind(minimum_height=self.expenses_box.setter("height"))

        # Header
        self.add_widget(Label(text="Operacional", font_size=20, size_hint_y=None, height=30))
        self.status = Label(text="", size_hint_y=None, height=26)
        self.pending_label = Label(text="", size_hint_y=None, height=20, font_size=11,
                                    color=(0.9, 0.6, 0.1, 1))
        self.add_widget(self.status)
        self.add_widget(self.pending_label)

        # Sub-navigation + content
        sub_nav = BoxLayout(size_hint_y=None, height=36, spacing=2)
        self.sub_content = ScreenManager()

        for label, name, builder in [
            ("Produtos", "produtos", self._build_produtos),
            ("Fornecedores", "fornecedores", self._build_fornecedores),
            ("Compras", "compras", self._build_compras),
            ("Despesas", "despesas", self._build_despesas),
            ("Estoque", "movimentacoes", self._build_movimentacoes),
        ]:
            s = Screen(name=name)
            s.add_widget(builder())
            self.sub_content.add_widget(s)
            btn = Button(text=label)
            btn.bind(on_press=lambda _, n=name: setattr(self.sub_content, "current", n))
            sub_nav.add_widget(btn)

        self.add_widget(sub_nav)
        self.add_widget(self.sub_content)
        Clock.schedule_once(lambda _: self.load(), 0.2)

    # ------------------------------------------------------------------ helpers

    def _update_pending_label(self):
        count = len(self.queue.get_pending())
        self.pending_label.text = f"{count} pendencia(s) offline" if count else ""

    def _scroll_section(self, inner_box):
        scroll = ScrollView()
        scroll.add_widget(inner_box)
        return scroll

    # ------------------------------------------------------------------ produtos

    def _build_produtos(self):
        root = BoxLayout(orientation="vertical", spacing=6)

        # Produto form
        pf = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=196)
        self.sku = TextInput(hint_text="SKU *", multiline=False)
        self.name = TextInput(hint_text="Nome do produto *", multiline=False)
        self.cost = TextInput(hint_text="Custo", multiline=False, input_filter="float")
        self.price = TextInput(hint_text="Preco de venda", multiline=False, input_filter="float")
        save_btn = Button(text="Cadastrar produto", size_hint_y=None, height=38)
        save_btn.bind(on_press=self.create_product)
        for w in [self.sku, self.name, self.cost, self.price, save_btn]:
            pf.add_widget(w)
        root.add_widget(pf)

        # Venda form
        sf = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=196)
        self.sale_variant_id = TextInput(hint_text="ID da variante *", multiline=False)
        self.sale_qty = TextInput(hint_text="Quantidade *", multiline=False, input_filter="int")
        self.sale_price = TextInput(hint_text="Preco unitario *", multiline=False, input_filter="float")
        self.sale_cost = TextInput(hint_text="Custo unitario", multiline=False, input_filter="float")
        sale_btn = Button(text="Registrar venda", size_hint_y=None, height=38)
        sale_btn.bind(on_press=self.create_sale)
        for w in [self.sale_variant_id, self.sale_qty, self.sale_price, self.sale_cost, sale_btn]:
            sf.add_widget(w)
        root.add_widget(sf)

        # Upload de foto
        uf = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=126)
        self.photo_product_id = TextInput(hint_text="ID do produto para foto *", multiline=False)
        self.photo_path = TextInput(hint_text="Caminho do arquivo de imagem *", multiline=False)
        upload_btn = Button(text="Enviar foto", size_hint_y=None, height=38)
        upload_btn.bind(on_press=self.upload_photo)
        self.photo_status = Label(text="", size_hint_y=None, height=22, font_size=12)
        for w in [self.photo_product_id, self.photo_path, upload_btn, self.photo_status]:
            uf.add_widget(w)
        root.add_widget(uf)

        # Acoes
        actions = BoxLayout(size_hint_y=None, height=38, spacing=6)
        refresh = Button(text="Atualizar lista")
        refresh.bind(on_press=lambda *_: self.load())
        alerts = Button(text="Estoque baixo")
        alerts.bind(on_press=lambda *_: self.load_alerts())
        actions.add_widget(refresh)
        actions.add_widget(alerts)
        root.add_widget(actions)

        root.add_widget(self._scroll_section(self.products_box))
        return root

    def load(self):
        data, _ = self.cache.get(_CACHE_KEY)
        if data is not None:
            self._render_products(data)
            self.status.text = "[cache] Atualizando..."
        else:
            self.status.text = "Carregando produtos..."
        self._update_pending_label()
        Clock.schedule_once(lambda _: self._load_products(), 0.1)

    def _load_products(self):
        try:
            products = self.api.get("/products")
            self.cache.set(_CACHE_KEY, products, _CACHE_TTL)
            self._render_products(products)
            self.status.text = ""
        except ApiError as exc:
            if not self.status.text.startswith("[cache]"):
                self.status.text = str(exc)

    def _render_products(self, products):
        self.products_box.clear_widgets()
        if not products:
            self.products_box.add_widget(
                Label(text="Nenhum produto cadastrado.", size_hint_y=None, height=28))
            return
        for p in products:
            stock = sum(v.get("stock_quantity", 0) for v in p.get("variants", []))
            self.products_box.add_widget(Label(
                text=f"{p['sku']} — {p['name']} | est: {stock} | R$ {p['sale_price']}",
                size_hint_y=None, height=28))
            for v in p.get("variants", []):
                self.products_box.add_widget(Label(
                    text=f"  {v['id']} | {v['size']}/{v['color']} | {v['stock_quantity']} un.",
                    size_hint_y=None, height=24))

    def load_alerts(self):
        try:
            alerts = self.api.get("/stock/alerts")
            self.products_box.clear_widgets()
            if not alerts:
                self.products_box.add_widget(
                    Label(text="Sem alertas de estoque.", size_hint_y=None, height=28))
            for a in alerts:
                self.products_box.add_widget(Label(
                    text=f"{a['product_name']} {a['size']}/{a['color']} — {a['stock']} un.",
                    size_hint_y=None, height=28))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def create_product(self, *_):
        try:
            payload = {
                "sku": _req(self.sku.text, "SKU"),
                "name": _req(self.name.text, "Nome"),
                "cost_price": _num(self.cost.text or "0", "Custo"),
                "sale_price": _num(self.price.text or "0", "Preco de venda"),
                "variants": [{"size": "Unico", "color": "Unico", "stock_quantity": 0}],
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/products", payload)
            self.status.text = "Produto cadastrado."
            self.sku.text = self.name.text = self.cost.text = self.price.text = ""
            self.cache.invalidate(_CACHE_KEY)
            self.load()
        except ConnectionApiError:
            self.queue.enqueue("create_product", payload)
            self.status.text = "Salvo offline. Sera enviado ao reconectar."
            self.sku.text = self.name.text = self.cost.text = self.price.text = ""
            self._update_pending_label()
        except ApiError as exc:
            self.status.text = str(exc)

    def create_sale(self, *_):
        try:
            payload = {
                "channel": "loja",
                "items": [{
                    "variant_id": _req(self.sale_variant_id.text, "ID da variante"),
                    "quantity": _num(self.sale_qty.text, "Quantidade", int),
                    "unit_price": _num(self.sale_price.text, "Preco unitario"),
                    "unit_cost": _num(self.sale_cost.text or "0", "Custo unitario"),
                }],
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/sales", payload)
            self.status.text = "Venda registrada."
            self.sale_variant_id.text = self.sale_qty.text = self.sale_price.text = self.sale_cost.text = ""
            self.cache.invalidate(_CACHE_KEY)
            self.load()
        except ConnectionApiError:
            self.queue.enqueue("create_sale", payload)
            self.status.text = "Salvo offline. Sera enviado ao reconectar."
            self.sale_variant_id.text = self.sale_qty.text = self.sale_price.text = self.sale_cost.text = ""
            self._update_pending_label()
        except ApiError as exc:
            self.status.text = str(exc)

    def upload_photo(self, *_):
        try:
            product_id = _req(self.photo_product_id.text, "ID do produto")
            file_path = _req(self.photo_path.text, "Caminho da imagem")
        except ValueError as exc:
            self.photo_status.text = str(exc)
            return
        self.photo_status.text = "Enviando..."
        Clock.schedule_once(lambda _: self._do_upload(product_id, file_path), 0.1)

    def _do_upload(self, product_id, file_path):
        try:
            self.api.upload(f"/products/{product_id}/photos", file_path)
            self.photo_status.text = "Foto adicionada."
            self.photo_product_id.text = self.photo_path.text = ""
        except (ApiError, OSError) as exc:
            self.photo_status.text = f"Erro — {exc}. Tente novamente."

    # ------------------------------------------------------------------ fornecedores

    def _build_fornecedores(self):
        root = BoxLayout(orientation="vertical", spacing=6)

        form = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=196)
        self.sup_nome = TextInput(hint_text="Nome *", multiline=False)
        self.sup_contato = TextInput(hint_text="Contato", multiline=False)
        self.sup_telefone = TextInput(hint_text="Telefone", multiline=False)
        self.sup_email = TextInput(hint_text="Email", multiline=False)
        sup_btn = Button(text="Cadastrar fornecedor", size_hint_y=None, height=38)
        sup_btn.bind(on_press=self.create_supplier)
        for w in [self.sup_nome, self.sup_contato, self.sup_telefone, self.sup_email, sup_btn]:
            form.add_widget(w)
        root.add_widget(form)

        refresh = Button(text="Atualizar fornecedores", size_hint_y=None, height=38)
        refresh.bind(on_press=lambda *_: self.load_suppliers())
        root.add_widget(refresh)
        root.add_widget(self._scroll_section(self.suppliers_box))
        return root

    def load_suppliers(self):
        self.status.text = "Carregando fornecedores..."
        Clock.schedule_once(lambda _: self._load_suppliers(), 0.1)

    def _load_suppliers(self):
        try:
            suppliers = self.api.get("/suppliers")
            self.suppliers_box.clear_widgets()
            if not suppliers:
                self.suppliers_box.add_widget(
                    Label(text="Nenhum fornecedor cadastrado.", size_hint_y=None, height=28))
            for s in suppliers:
                self.suppliers_box.add_widget(Label(
                    text=f"ID {s['id']} | {s['name']} | {s.get('phone') or '—'}",
                    size_hint_y=None, height=28))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def create_supplier(self, *_):
        try:
            payload = {
                "name": _req(self.sup_nome.text, "Nome"),
                "contact": self.sup_contato.text.strip() or None,
                "phone": self.sup_telefone.text.strip() or None,
                "email": self.sup_email.text.strip() or None,
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/suppliers", payload)
            self.status.text = "Fornecedor cadastrado."
            self.sup_nome.text = self.sup_contato.text = self.sup_telefone.text = self.sup_email.text = ""
            self.load_suppliers()
        except ApiError as exc:
            self.status.text = str(exc)

    # ------------------------------------------------------------------ compras

    def _build_compras(self):
        root = BoxLayout(orientation="vertical", spacing=6)

        form = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=234)
        self.po_supplier_id = TextInput(hint_text="ID do fornecedor *", multiline=False)
        self.po_variant_id = TextInput(hint_text="ID da variante *", multiline=False)
        self.po_qty = TextInput(hint_text="Quantidade *", multiline=False, input_filter="int")
        self.po_unit_cost = TextInput(hint_text="Custo unitario *", multiline=False, input_filter="float")
        self.po_notes = TextInput(hint_text="Observacoes", multiline=False)
        po_btn = Button(text="Registrar compra", size_hint_y=None, height=38)
        po_btn.bind(on_press=self.create_purchase)
        for w in [self.po_supplier_id, self.po_variant_id, self.po_qty, self.po_unit_cost, self.po_notes, po_btn]:
            form.add_widget(w)
        root.add_widget(form)

        receive_row = BoxLayout(size_hint_y=None, height=38, spacing=6)
        self.po_receive_id = TextInput(hint_text="ID da compra para receber", multiline=False)
        receive_btn = Button(text="Receber", size_hint_x=0.28)
        receive_btn.bind(on_press=self.receive_purchase)
        receive_row.add_widget(self.po_receive_id)
        receive_row.add_widget(receive_btn)
        root.add_widget(receive_row)

        refresh = Button(text="Atualizar compras", size_hint_y=None, height=38)
        refresh.bind(on_press=lambda *_: self.load_purchases())
        root.add_widget(refresh)
        root.add_widget(self._scroll_section(self.purchases_box))
        return root

    def load_purchases(self):
        self.status.text = "Carregando compras..."
        Clock.schedule_once(lambda _: self._load_purchases(), 0.1)

    def _load_purchases(self):
        try:
            purchases = self.api.get("/purchases")
            self.purchases_box.clear_widgets()
            if not purchases:
                self.purchases_box.add_widget(
                    Label(text="Nenhuma compra registrada.", size_hint_y=None, height=28))
            for p in purchases:
                self.purchases_box.add_widget(Label(
                    text=f"ID {p['id']} | {p.get('order_date', '—')} | {p.get('status', '—')}",
                    size_hint_y=None, height=28))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def create_purchase(self, *_):
        try:
            payload = {
                "supplier_id": _num(self.po_supplier_id.text, "ID do fornecedor", int),
                "notes": self.po_notes.text.strip() or None,
                "items": [{
                    "variant_id": _req(self.po_variant_id.text, "ID da variante"),
                    "quantity": _num(self.po_qty.text, "Quantidade", int),
                    "unit_cost": _num(self.po_unit_cost.text, "Custo unitario"),
                }],
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/purchases", payload)
            self.status.text = "Compra registrada."
            self.po_supplier_id.text = self.po_variant_id.text = ""
            self.po_qty.text = self.po_unit_cost.text = self.po_notes.text = ""
            self.load_purchases()
        except ApiError as exc:
            self.status.text = str(exc)

    def receive_purchase(self, *_):
        try:
            po_id = _req(self.po_receive_id.text, "ID da compra")
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.put(f"/purchases/{po_id}/receive", {})
            self.status.text = f"Compra {po_id} recebida."
            self.po_receive_id.text = ""
            self.load_purchases()
        except ApiError as exc:
            self.status.text = str(exc)

    # ------------------------------------------------------------------ despesas

    def _build_despesas(self):
        root = BoxLayout(orientation="vertical", spacing=6)

        form = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=196)
        self.exp_date = TextInput(hint_text="Data (AAAA-MM-DD, padrao hoje)", multiline=False)
        self.exp_category = TextInput(hint_text="Categoria *", multiline=False)
        self.exp_amount = TextInput(hint_text="Valor *", multiline=False, input_filter="float")
        self.exp_description = TextInput(hint_text="Descricao", multiline=False)
        exp_btn = Button(text="Registrar despesa", size_hint_y=None, height=38)
        exp_btn.bind(on_press=self.create_expense)
        for w in [self.exp_date, self.exp_category, self.exp_amount, self.exp_description, exp_btn]:
            form.add_widget(w)
        root.add_widget(form)

        delete_row = BoxLayout(size_hint_y=None, height=38, spacing=6)
        self.exp_delete_id = TextInput(hint_text="ID da despesa para excluir", multiline=False)
        delete_btn = Button(text="Excluir", size_hint_x=0.28)
        delete_btn.bind(on_press=self.delete_expense)
        delete_row.add_widget(self.exp_delete_id)
        delete_row.add_widget(delete_btn)
        root.add_widget(delete_row)

        refresh = Button(text="Atualizar despesas", size_hint_y=None, height=38)
        refresh.bind(on_press=lambda *_: self.load_expenses())
        root.add_widget(refresh)
        root.add_widget(self._scroll_section(self.expenses_box))
        return root

    def load_expenses(self):
        self.status.text = "Carregando despesas..."
        Clock.schedule_once(lambda _: self._load_expenses(), 0.1)

    def _load_expenses(self):
        try:
            expenses = self.api.get("/expenses")
            self.expenses_box.clear_widgets()
            if not expenses:
                self.expenses_box.add_widget(
                    Label(text="Nenhuma despesa registrada.", size_hint_y=None, height=28))
            for e in expenses:
                self.expenses_box.add_widget(Label(
                    text=f"ID {e['id']} | {e['date']} | {e['category']} | R$ {e['amount']}",
                    size_hint_y=None, height=28))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def create_expense(self, *_):
        try:
            payload = {
                "date": self.exp_date.text.strip() or str(_today_date.today()),
                "category": _req(self.exp_category.text, "Categoria"),
                "amount": _num(self.exp_amount.text, "Valor"),
                "description": self.exp_description.text.strip() or None,
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/expenses", payload)
            self.status.text = "Despesa registrada."
            self.exp_date.text = self.exp_category.text = self.exp_amount.text = self.exp_description.text = ""
            self.load_expenses()
        except ApiError as exc:
            self.status.text = str(exc)

    def delete_expense(self, *_):
        try:
            exp_id = _req(self.exp_delete_id.text, "ID da despesa")
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.delete(f"/expenses/{exp_id}")
            self.status.text = f"Despesa {exp_id} excluida."
            self.exp_delete_id.text = ""
            self.load_expenses()
        except ApiError as exc:
            self.status.text = str(exc)

    # ------------------------------------------------------------------ movimentacoes

    def _build_movimentacoes(self):
        root = BoxLayout(orientation="vertical", spacing=6)

        form = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=234)
        self.mov_variant_id = TextInput(hint_text="ID da variante *", multiline=False)
        self.mov_type = TextInput(
            hint_text="Tipo * (entrada / saida / ajuste / devolucao)", multiline=False)
        self.mov_qty = TextInput(hint_text="Quantidade *", multiline=False, input_filter="int")
        self.mov_unit_cost = TextInput(hint_text="Custo unitario", multiline=False, input_filter="float")
        self.mov_notes = TextInput(hint_text="Observacoes", multiline=False)
        mov_btn = Button(text="Registrar movimentacao", size_hint_y=None, height=38)
        mov_btn.bind(on_press=self.create_movement)
        for w in [self.mov_variant_id, self.mov_type, self.mov_qty,
                  self.mov_unit_cost, self.mov_notes, mov_btn]:
            form.add_widget(w)
        root.add_widget(form)
        return root

    def create_movement(self, *_):
        try:
            mov_type = _req(self.mov_type.text, "Tipo")
            if mov_type not in _VALID_MOV_TYPES:
                raise ValueError(f"Tipo invalido. Use: {', '.join(sorted(_VALID_MOV_TYPES))}")
            payload = {
                "variant_id": _req(self.mov_variant_id.text, "ID da variante"),
                "movement_type": mov_type,
                "quantity": _num(self.mov_qty.text, "Quantidade", int),
                "unit_cost": float(self.mov_unit_cost.text) if self.mov_unit_cost.text.strip() else None,
                "notes": self.mov_notes.text.strip() or None,
            }
        except ValueError as exc:
            self.status.text = str(exc)
            return
        try:
            self.api.post("/stock/movements", payload)
            self.status.text = "Movimentacao registrada."
            self.mov_variant_id.text = self.mov_type.text = self.mov_qty.text = ""
            self.mov_unit_cost.text = self.mov_notes.text = ""
        except ApiError as exc:
            self.status.text = str(exc)
