"""Tela de análises do app mobile.

Agrupa dashboard, rankings, visões por tamanho/canal, sugestões de compra e DRE
em subtelas Kivy simples, consumindo as rotas `/analytics` do backend.
"""

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

from services.api_client import ApiError
from storage.cache import LocalCache

_CACHE_KEY = "dashboard"
_CACHE_TTL = 300


def _result_label():
    """Cria um label com quebra automática para resultados textuais longos."""

    lbl = Label(text="Toque em Atualizar para carregar.", halign="left", valign="top")
    lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
    return lbl


class AnalyticsScreen(BoxLayout):
    """Tela principal do módulo de análise no aplicativo Kivy."""

    def __init__(self, api, **kwargs):
        """Monta subnavegação e agenda o carregamento inicial do dashboard."""

        super().__init__(orientation="vertical", padding=8, spacing=4, **kwargs)
        self.api = api
        self.cache = LocalCache()

        self.add_widget(Label(text="Analise", font_size=20, size_hint_y=None, height=30))
        self.cache_label = Label(text="", size_hint_y=None, height=20, font_size=11,
                                  color=(0.6, 0.6, 0.6, 1))
        self.add_widget(self.cache_label)

        sub_nav = BoxLayout(size_hint_y=None, height=36, spacing=2)
        self.sub_content = ScreenManager()

        for label, name, builder in [
            ("Dashboard", "dashboard", self._build_dashboard),
            ("Top Prod.", "top_produtos", self._build_top_produtos),
            ("Tamanho", "por_tamanho", self._build_por_tamanho),
            ("Canal", "por_canal", self._build_por_canal),
            ("Sugestoes", "sugestoes", self._build_sugestoes),
            ("DRE", "dre", self._build_dre),
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

    # ------------------------------------------------------------------ dashboard

    def _build_dashboard(self):
        """Cria a seção de dashboard com botão de atualização."""

        box = BoxLayout(orientation="vertical", spacing=6)
        refresh = Button(text="Atualizar dashboard", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self.load())
        self.dash_content = Label(text="", halign="left", valign="top")
        self.dash_content.bind(size=lambda i, v: setattr(i, "text_size", v))
        box.add_widget(refresh)
        box.add_widget(self.dash_content)
        return box

    def load(self):
        """Mostra dashboard em cache imediatamente e atualiza em segundo momento."""

        data, _ = self.cache.get(_CACHE_KEY)
        if data is not None:
            self._render_dashboard(data)
            self.cache_label.text = "[cache] Atualizando..."
        else:
            self.dash_content.text = "Carregando..."
            self.cache_label.text = ""
        Clock.schedule_once(lambda _: self._load_dashboard(), 0.1)

    def _load_dashboard(self):
        """Busca o dashboard na API e atualiza cache/renderização."""

        try:
            data = self.api.get("/analytics/dashboard")
            self.cache.set(_CACHE_KEY, data, _CACHE_TTL)
            self._render_dashboard(data)
            self.cache_label.text = ""
        except ApiError as exc:
            if not self.cache_label.text:
                self.dash_content.text = str(exc)

    def _render_dashboard(self, data):
        """Transforma o dicionário do backend em texto compacto para a tela."""

        self.dash_content.text = (
            f"Receita hoje: R$ {data['today_revenue']:.2f}\n"
            f"Vendas hoje: {data['today_count']}\n"
            f"Receita mes: R$ {data['month_revenue']:.2f}\n"
            f"CMV mes: R$ {data['month_cogs']:.2f}\n"
            f"Lucro liquido: R$ {data['net_profit']:.2f}\n"
            f"Margem: {data['margin_pct']}%\n"
            f"Alertas de estoque: {data['stock_alerts']}\n"
            f"Unidades em estoque: {data['stock_units']}"
        )

    # ------------------------------------------------------------------ top produtos

    def _build_top_produtos(self):
        """Cria a seção de ranking de produtos."""

        box = BoxLayout(orientation="vertical", spacing=6)
        self.top_status = Label(text="", size_hint_y=None, height=24, font_size=12)
        self.top_content = _result_label()
        refresh = Button(text="Atualizar top produtos", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self._fetch_top_produtos())
        box.add_widget(refresh)
        box.add_widget(self.top_status)
        box.add_widget(self.top_content)
        return box

    def _fetch_top_produtos(self):
        """Agenda a busca do ranking de produtos."""

        self.top_status.text = "Buscando..."
        Clock.schedule_once(lambda _: self._load_top_produtos(), 0.1)

    def _load_top_produtos(self):
        """Carrega e renderiza os produtos mais vendidos."""

        try:
            data = self.api.get("/analytics/top-products", {"days": 30})
            if not data:
                self.top_content.text = "Sem dados."
            else:
                lines = []
                for i, p in enumerate(data, 1):
                    name = p.get("name") or p.get("product_name") or "?"
                    qty = p.get("total_qty") or p.get("quantity") or "?"
                    lines.append(f"{i}. {name} — {qty} un.")
                self.top_content.text = "\n".join(lines)
            self.top_status.text = ""
        except ApiError as exc:
            self.top_status.text = str(exc)

    # ------------------------------------------------------------------ por tamanho

    def _build_por_tamanho(self):
        """Cria a seção de vendas por tamanho."""

        box = BoxLayout(orientation="vertical", spacing=6)
        self.size_status = Label(text="", size_hint_y=None, height=24, font_size=12)
        self.size_content = _result_label()
        refresh = Button(text="Atualizar por tamanho", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self._fetch_por_tamanho())
        box.add_widget(refresh)
        box.add_widget(self.size_status)
        box.add_widget(self.size_content)
        return box

    def _fetch_por_tamanho(self):
        """Agenda a busca de vendas por tamanho."""

        self.size_status.text = "Buscando..."
        Clock.schedule_once(lambda _: self._load_por_tamanho(), 0.1)

    def _load_por_tamanho(self):
        """Carrega e renderiza quantidades vendidas por tamanho."""

        try:
            data = self.api.get("/analytics/by-size", {"days": 30})
            if not data:
                self.size_content.text = "Sem dados."
            else:
                lines = []
                for row in data:
                    size = row.get("size") or "?"
                    qty = row.get("total_qty") or row.get("quantity") or "?"
                    lines.append(f"Tamanho {size} — {qty} un.")
                self.size_content.text = "\n".join(lines)
            self.size_status.text = ""
        except ApiError as exc:
            self.size_status.text = str(exc)

    # ------------------------------------------------------------------ por canal

    def _build_por_canal(self):
        """Cria a seção de vendas por canal."""

        box = BoxLayout(orientation="vertical", spacing=6)
        self.canal_status = Label(text="", size_hint_y=None, height=24, font_size=12)
        self.canal_content = _result_label()
        refresh = Button(text="Atualizar por canal", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self._fetch_por_canal())
        box.add_widget(refresh)
        box.add_widget(self.canal_status)
        box.add_widget(self.canal_content)
        return box

    def _fetch_por_canal(self):
        """Agenda a busca de vendas por canal."""

        self.canal_status.text = "Buscando..."
        Clock.schedule_once(lambda _: self._load_por_canal(), 0.1)

    def _load_por_canal(self):
        """Carrega e renderiza resultados agrupados por canal."""

        try:
            data = self.api.get("/analytics/by-channel", {"days": 30})
            if not data:
                self.canal_content.text = "Sem dados."
            else:
                lines = []
                for row in data:
                    channel = row.get("channel") or "?"
                    qty = row.get("total_qty") or row.get("quantity") or "?"
                    revenue = row.get("revenue") or row.get("total") or "?"
                    lines.append(f"{channel} — {qty} un. | R$ {revenue}")
                self.canal_content.text = "\n".join(lines)
            self.canal_status.text = ""
        except ApiError as exc:
            self.canal_status.text = str(exc)

    # ------------------------------------------------------------------ sugestoes de compra

    def _build_sugestoes(self):
        """Cria a seção de sugestões de compra."""

        box = BoxLayout(orientation="vertical", spacing=6)
        self.sug_status = Label(text="", size_hint_y=None, height=24, font_size=12)
        self.sug_content = _result_label()
        refresh = Button(text="Atualizar sugestoes de compra", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self._fetch_sugestoes())
        box.add_widget(refresh)
        box.add_widget(self.sug_status)
        box.add_widget(self.sug_content)
        return box

    def _fetch_sugestoes(self):
        """Agenda a busca de sugestões de reposição."""

        self.sug_status.text = "Buscando..."
        Clock.schedule_once(lambda _: self._load_sugestoes(), 0.1)

    def _load_sugestoes(self):
        """Carrega e renderiza sugestões de compra vindas do backend."""

        try:
            data = self.api.get("/analytics/purchase-suggestions")
            if not data:
                self.sug_content.text = "Sem sugestoes no momento."
            else:
                lines = []
                for row in data:
                    name = row.get("product_name") or "?"
                    size = row.get("size") or ""
                    stock = row.get("stock") or row.get("current_stock") or "?"
                    suggested = row.get("suggested_qty") or row.get("quantity") or "?"
                    lines.append(f"{name} {size} — est: {stock} | sugerido: {suggested} un.")
                self.sug_content.text = "\n".join(lines)
            self.sug_status.text = ""
        except ApiError as exc:
            self.sug_status.text = str(exc)

    # ------------------------------------------------------------------ DRE

    def _build_dre(self):
        """Cria a seção de DRE com filtros de mês e ano."""

        box = BoxLayout(orientation="vertical", spacing=6)

        row = BoxLayout(size_hint_y=None, height=38, spacing=6)
        self.dre_month = TextInput(hint_text="Mes (1-12)", multiline=False, input_filter="int")
        self.dre_year = TextInput(hint_text="Ano (ex: 2026)", multiline=False, input_filter="int")
        row.add_widget(self.dre_month)
        row.add_widget(self.dre_year)
        box.add_widget(row)

        self.dre_status = Label(text="", size_hint_y=None, height=24, font_size=12)
        self.dre_content = _result_label()
        refresh = Button(text="Atualizar DRE", size_hint_y=None, height=40)
        refresh.bind(on_press=lambda *_: self._fetch_dre())
        box.add_widget(refresh)
        box.add_widget(self.dre_status)
        box.add_widget(self.dre_content)
        return box

    def _fetch_dre(self):
        """Valida filtros e agenda a busca do DRE."""

        month = self.dre_month.text.strip()
        year = self.dre_year.text.strip()
        if not month or not year:
            self.dre_status.text = "Informe mes e ano."
            return
        self.dre_status.text = "Buscando..."
        Clock.schedule_once(lambda _: self._load_dre(month, year), 0.1)

    def _load_dre(self, month, year):
        """Carrega e renderiza o DRE do período solicitado."""

        try:
            data = self.api.get("/analytics/finance/dre", {"month": month, "year": year})
            self.dre_content.text = (
                f"Receita bruta:   R$ {data.get('gross_revenue', 0):.2f}\n"
                f"CMV:             R$ {data.get('cogs', 0):.2f}\n"
                f"Lucro bruto:     R$ {data.get('gross_profit', 0):.2f}\n"
                f"Despesas:        R$ {data.get('expenses', 0):.2f}\n"
                f"Lucro liquido:   R$ {data.get('net_profit', 0):.2f}\n"
                f"Margem liquida:  {data.get('net_margin_pct', 0):.1f}%"
            )
            self.dre_status.text = f"DRE {month}/{year}"
        except ApiError as exc:
            self.dre_status.text = str(exc)
