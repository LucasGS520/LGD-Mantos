import { AppBar, BottomNav, ScreenBody } from "../components/Chrome";
import { Session } from "../modules/auth/session";
import { useData } from "../shared/hooks/useData";
import { Card, Section } from "../shared/ui";
import { Button } from "../shared/ui/Button";
import { useNav } from "./nav";
import { systemApi } from "./systemApi";
export function MoreScreen() {
  const { navigate, logout } = useNav();
  const { data } = useData(() => systemApi.health());
  return (
    <>
      <AppBar title="Mais" />
      <ScreenBody>
        <Card>
          <h3>LGD Mantos</h3>
          <p>Uma loja · acesso único do dono</p>
          <Button onClick={() => navigate("auxiliaries")}>
            Fornecedores, categorias, canais e formas de pagamento
          </Button>
        </Card>
        <Section title="Acesso e sistema">
          <p>
            Sessão válida até {Session.getExpiry()?.toLocaleString("pt-BR")}
          </p>
          <p>
            Banco: {data?.database || "verificando"} · API{" "}
            {data?.version || "—"} · App {__APP_VERSION__}
          </p>
          <Button onClick={logout}>Sair</Button>
        </Section>
      </ScreenBody>
      <BottomNav active="mais" />
    </>
  );
}
