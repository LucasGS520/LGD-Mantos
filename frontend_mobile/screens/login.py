from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from services.api_client import ApiError


class LoginScreen(BoxLayout):
    def __init__(self, api, session, on_login, **kwargs):
        super().__init__(orientation="vertical", padding=24, spacing=12, **kwargs)
        self.api = api
        self.session = session
        self.on_login = on_login

        self.add_widget(Label(text="LGD Mantos", font_size=28, size_hint_y=None, height=52))
        self.add_widget(Label(text="Gestao interna mobile", size_hint_y=None, height=32))
        self.password = TextInput(password=True, multiline=False, hint_text="Senha de acesso")
        self.status = Label(text="", size_hint_y=None, height=42)
        self.button = Button(text="Entrar", size_hint_y=None, height=48)
        self.button.bind(on_press=self.submit)
        self.add_widget(self.password)
        self.add_widget(self.button)
        self.add_widget(self.status)

    def submit(self, *_):
        self.status.text = "Entrando..."
        self.button.disabled = True
        Clock.schedule_once(lambda _: self._login(), 0.1)

    def _login(self):
        try:
            token = self.api.login(self.password.text)
            self.session.save_token(token)
            self.status.text = ""
            self.on_login()
        except ApiError as exc:
            self.status.text = str(exc)
        finally:
            self.button.disabled = False
