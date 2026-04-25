"""Tela de marketing com geração de textos via IA."""

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from services.api_client import ApiError


class MarketingScreen(BoxLayout):
    """Permite pedir copys sociais e campanhas ao backend."""

    def __init__(self, api, **kwargs):
        """Monta campo de prompt, botões de ação e área de resultado."""

        super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)
        self.api = api
        self.add_widget(Label(text="Marketing IA", font_size=22, size_hint_y=None, height=36))
        self.prompt = TextInput(
            hint_text="Ex: Crie uma legenda para divulgar camisetas oversized pretas",
            multiline=True,
            size_hint_y=None,
            height=100,
        )
        self.result = Label(text="", halign="left", valign="top")
        self.result.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        buttons = BoxLayout(size_hint_y=None, height=44, spacing=8)
        social = Button(text="Copy social")
        social.bind(on_press=lambda *_: self.generate("/marketing/social-copy"))
        campaign = Button(text="Campanha")
        campaign.bind(on_press=lambda *_: self.generate("/marketing/campaign-suggestion"))
        buttons.add_widget(social)
        buttons.add_widget(campaign)
        self.add_widget(self.prompt)
        self.add_widget(buttons)
        self.add_widget(self.result)

    def generate(self, path: str):
        """Agenda a chamada de IA para manter a interface responsiva."""

        self.result.text = "Gerando..."
        Clock.schedule_once(lambda _: self._generate(path), 0.1)

    def _generate(self, path: str):
        """Envia o prompt para a rota escolhida e renderiza a resposta."""

        try:
            data = self.api.post(path, {"message": self.prompt.text, "product_ids": []})
            self.result.text = data.get("response", "")
        except ApiError as exc:
            self.result.text = str(exc)
