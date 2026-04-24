from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from services.api_client import ApiError


class AnalyticsScreen(BoxLayout):
    def __init__(self, api, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)
        self.api = api
        self.title = Label(text="Analise", font_size=22, size_hint_y=None, height=36)
        self.content = Label(text="", halign="left", valign="top")
        self.content.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        refresh = Button(text="Atualizar dashboard", size_hint_y=None, height=44)
        refresh.bind(on_press=lambda *_: self.load())
        self.add_widget(self.title)
        self.add_widget(refresh)
        self.add_widget(self.content)
        Clock.schedule_once(lambda _: self.load(), 0.2)

    def load(self):
        self.content.text = "Carregando..."
        Clock.schedule_once(lambda _: self._load(), 0.1)

    def _load(self):
        try:
            data = self.api.get("/analytics/dashboard")
            self.content.text = (
                f"Receita hoje: R$ {data['today_revenue']:.2f}\n"
                f"Vendas hoje: {data['today_count']}\n"
                f"Receita mes: R$ {data['month_revenue']:.2f}\n"
                f"CMV mes: R$ {data['month_cogs']:.2f}\n"
                f"Lucro liquido: R$ {data['net_profit']:.2f}\n"
                f"Margem: {data['margin_pct']}%\n"
                f"Alertas de estoque: {data['stock_alerts']}\n"
                f"Unidades em estoque: {data['stock_units']}"
            )
        except ApiError as exc:
            self.content.text = str(exc)
