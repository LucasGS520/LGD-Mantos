from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

from screens.analytics import AnalyticsScreen
from screens.login import LoginScreen
from screens.marketing import MarketingScreen
from screens.operational import OperationalScreen
from services.api_client import ApiClient
from services.sync import SyncService
from storage.offline_queue import OfflineQueue
from storage.session import SessionStore


class LGDMantosApp(App):
    title = "LGD Mantos"

    def build(self):
        self.session = SessionStore()
        self.api = ApiClient(token=self.session.load_token())
        self.api.on_unauthorized = self._handle_unauthorized
        self.queue = OfflineQueue()
        self.sync_service = SyncService(self.api, self.queue)
        self.manager = ScreenManager()
        self._build_screens()
        if self.session.is_valid():
            self.manager.current = "home"
            Clock.schedule_once(lambda _: self.sync_service.sync(), 1.5)
        else:
            self.manager.current = "login"
        return self.manager

    def _build_screens(self):
        login = Screen(name="login")
        login.add_widget(LoginScreen(self.api, self.session, self.show_home))
        self.manager.add_widget(login)

        home = Screen(name="home")
        home.add_widget(self._home_layout())
        self.manager.add_widget(home)

    def _home_layout(self):
        root = BoxLayout(orientation="vertical")
        nav = BoxLayout(size_hint_y=None, height=48, spacing=4)
        content = ScreenManager()

        operational = Screen(name="operational")
        operational.add_widget(OperationalScreen(self.api, self.queue))
        analytics = Screen(name="analytics")
        analytics.add_widget(AnalyticsScreen(self.api))
        marketing = Screen(name="marketing")
        marketing.add_widget(MarketingScreen(self.api))

        content.add_widget(operational)
        content.add_widget(analytics)
        content.add_widget(marketing)

        for label, target in [
            ("Operacao", "operational"),
            ("Analise", "analytics"),
            ("Marketing", "marketing"),
        ]:
            button = Button(text=label)
            button.bind(on_press=lambda _, screen=target: setattr(content, "current", screen))
            nav.add_widget(button)

        logout = Button(text="Sair")
        logout.bind(on_press=lambda *_: self.logout())
        nav.add_widget(logout)

        root.add_widget(nav)
        root.add_widget(content)
        return root

    def show_home(self):
        self.manager.current = "home"
        Clock.schedule_once(lambda _: self.sync_service.sync(), 0.5)

    def logout(self):
        self.session.clear()
        self.api.set_token(None)
        self.manager.current = "login"

    def _handle_unauthorized(self):
        self.session.clear()
        self.api.set_token(None)
        if self.manager.current != "login":
            self.manager.current = "login"


if __name__ == "__main__":
    LGDMantosApp().run()
