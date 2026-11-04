import {
useState
} from "react";
import { AppBar,BottomNav,ScreenBody } from "../../components/Chrome";
import { Card,ErrorBody,LoadingBody,Section } from "../../components/UI";
import { useData } from "../../hooks/useData";
import { useNav } from "../../nav";
import {
api,
type Auxiliary
} from "../../services/domain";
import { Session } from "../../services/session";
import "../../styles/workspace.css";

import {
Button,
ErrorMessage,
Field,
History,
Select,
auxLabels,
errorText
} from "./Shared";

export function AuxiliaryScreen() {
  const { data, loading, error, reload } = useData(() =>
    api.get<Auxiliary[]>("/auxiliaries"),
  );
  const [kind, setKind] = useState("supplier");
  const [editing, setEditing] = useState<Auxiliary | null>(null);
  return (
    <>
      <AppBar title="Cadastros auxiliares" back />
      <ScreenBody>
        <Select
          label="Cadastro"
          value={kind}
          onChange={(value) => {
            setKind(value);
            setEditing(null);
          }}
          options={Object.entries(auxLabels).map(([id, name]) => ({
            id,
            name,
          }))}
        />
        <AuxiliaryForm
          key={editing?.id || kind}
          kind={kind}
          editing={editing}
          onSaved={() => {
            setEditing(null);
            reload();
          }}
        />
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data
            ?.filter((a) => a.kind === kind)
            .map((a) => (
              <Card key={a.id}>
                <h3>
                  {a.name} {!a.active && "· desativado"}
                </h3>
                <p>{a.notes}</p>
                <Button onClick={() => setEditing(a)}>
                  Renomear ou desativar
                </Button>
                <History id={a.id} />
              </Card>
            ))
        )}
      </ScreenBody>
    </>
  );
}

function AuxiliaryForm({
  kind,
  editing,
  onSaved,
}: {
  kind: string;
  editing: Auxiliary | null;
  onSaved: () => void;
}) {
  const [name, setName] = useState(editing?.name || "");
  const [notes, setNotes] = useState(editing?.notes || "");
  const [active, setActive] = useState(editing?.active ?? true);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="form"
      onSubmit={async (e) => {
        e.preventDefault();
        if (busy) return;
        setBusy(true);
        setError(null);
        try {
          const body = {
            kind,
            name,
            notes: notes || null,
            active,
            ...(editing ? { version: editing.version, reason } : {}),
          };
          if (editing) await api.put(`/auxiliaries/${editing.id}`, body);
          else await api.post("/auxiliaries", body);
          setName("");
          setNotes("");
          onSaved();
        } catch (e) {
          setError(errorText(e));
        } finally {
          setBusy(false);
        }
      }}
    >
      <Field
        label={editing ? "Nome" : "Novo nome"}
        value={name}
        onChange={setName}
        required
      />
      <Field label="Observação opcional" value={notes} onChange={setNotes} />
      <label>
        <input
          type="checkbox"
          checked={active}
          onChange={(e) => setActive(e.target.checked)}
        />{" "}
        Ativo para novas operações
      </label>
      {editing && (
        <Field label="Motivo" value={reason} onChange={setReason} required />
      )}
      <ErrorMessage message={error} />
      <Button type="submit" disabled={busy}>
        {editing ? "Salvar alteração" : "Cadastrar"}
      </Button>
    </form>
  );
}

export function MoreScreen() {
  const { navigate, logout } = useNav();
  const { data } = useData(() =>
    api.get<{ database: string; version: string }>("/health"),
  );
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
