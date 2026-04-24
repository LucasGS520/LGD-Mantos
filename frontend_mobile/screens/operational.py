from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from services.api_client import ApiError


class OperationalScreen(BoxLayout):
    def __init__(self, api, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)
        self.api = api
        self.products_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.products_box.bind(minimum_height=self.products_box.setter("height"))

        self.add_widget(Label(text="Operacional", font_size=22, size_hint_y=None, height=36))
        self.status = Label(text="", size_hint_y=None, height=32)
        self.add_widget(self.status)

        form = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=220)
        self.sku = TextInput(hint_text="SKU", multiline=False)
        self.name = TextInput(hint_text="Nome do produto", multiline=False)
        self.cost = TextInput(hint_text="Custo", multiline=False, input_filter="float")
        self.price = TextInput(hint_text="Preco de venda", multiline=False, input_filter="float")
        save = Button(text="Cadastrar produto simples", size_hint_y=None, height=44)
        save.bind(on_press=self.create_product)
        for widget in [self.sku, self.name, self.cost, self.price, save]:
            form.add_widget(widget)
        self.add_widget(form)

        sale_form = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=220)
        self.sale_variant_id = TextInput(hint_text="ID da variante para venda", multiline=False)
        self.sale_qty = TextInput(hint_text="Quantidade", multiline=False, input_filter="int")
        self.sale_price = TextInput(hint_text="Preco unitario", multiline=False, input_filter="float")
        self.sale_cost = TextInput(hint_text="Custo unitario", multiline=False, input_filter="float")
        sale_button = Button(text="Registrar venda", size_hint_y=None, height=44)
        sale_button.bind(on_press=self.create_sale)
        for widget in [self.sale_variant_id, self.sale_qty, self.sale_price, self.sale_cost, sale_button]:
            sale_form.add_widget(widget)
        self.add_widget(sale_form)

        actions = BoxLayout(size_hint_y=None, height=44, spacing=8)
        refresh = Button(text="Atualizar produtos")
        refresh.bind(on_press=lambda *_: self.load())
        alerts = Button(text="Estoque baixo")
        alerts.bind(on_press=lambda *_: self.load_alerts())
        actions.add_widget(refresh)
        actions.add_widget(alerts)
        self.add_widget(actions)

        scroll = ScrollView()
        scroll.add_widget(self.products_box)
        self.add_widget(scroll)
        Clock.schedule_once(lambda _: self.load(), 0.2)

    def load(self):
        self.status.text = "Carregando produtos..."
        Clock.schedule_once(lambda _: self._load_products(), 0.1)

    def _load_products(self):
        try:
            products = self.api.get("/products")
            self.products_box.clear_widgets()
            if not products:
                self.products_box.add_widget(Label(text="Nenhum produto cadastrado.", size_hint_y=None, height=32))
            for product in products:
                stock = sum(item.get("stock_quantity", 0) for item in product.get("variants", []))
                text = f"{product['sku']} - {product['name']} | estoque: {stock} | R$ {product['sale_price']}"
                self.products_box.add_widget(Label(text=text, size_hint_y=None, height=34))
                for variant in product.get("variants", []):
                    variant_text = (
                        f"  {variant['id']} | {variant['size']}/{variant['color']} | "
                        f"{variant['stock_quantity']} un."
                    )
                    self.products_box.add_widget(Label(text=variant_text, size_hint_y=None, height=30))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def load_alerts(self):
        try:
            alerts = self.api.get("/stock/alerts")
            self.products_box.clear_widgets()
            if not alerts:
                self.products_box.add_widget(Label(text="Sem alertas de estoque.", size_hint_y=None, height=32))
            for alert in alerts:
                text = f"{alert['product_name']} {alert['size']}/{alert['color']} - {alert['stock']} un."
                self.products_box.add_widget(Label(text=text, size_hint_y=None, height=34))
            self.status.text = ""
        except ApiError as exc:
            self.status.text = str(exc)

    def create_product(self, *_):
        try:
            payload = {
                "sku": self.sku.text.strip(),
                "name": self.name.text.strip(),
                "cost_price": float(self.cost.text or 0),
                "sale_price": float(self.price.text or 0),
                "variants": [{"size": "Unico", "color": "Unico", "stock_quantity": 0}],
            }
            self.api.post("/products", payload)
            self.status.text = "Produto cadastrado."
            self.sku.text = self.name.text = self.cost.text = self.price.text = ""
            self.load()
        except (ApiError, ValueError) as exc:
            self.status.text = str(exc)

    def create_sale(self, *_):
        try:
            payload = {
                "channel": "loja",
                "items": [
                    {
                        "variant_id": self.sale_variant_id.text.strip(),
                        "quantity": int(self.sale_qty.text or 1),
                        "unit_price": float(self.sale_price.text or 0),
                        "unit_cost": float(self.sale_cost.text or 0),
                    }
                ],
            }
            self.api.post("/sales", payload)
            self.status.text = "Venda registrada."
            self.sale_variant_id.text = self.sale_qty.text = self.sale_price.text = self.sale_cost.text = ""
            self.load()
        except (ApiError, ValueError) as exc:
            self.status.text = str(exc)
