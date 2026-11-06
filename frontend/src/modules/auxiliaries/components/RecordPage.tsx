import type { ComponentType } from "react";
import { useState } from "react";
import { ScreenBody } from "../../../components/Chrome";
import { useData } from "../../../shared/hooks/useData";
import { Card, ErrorBody, LoadingBody } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { History } from "../../history";
import { type Auxiliary } from "../contracts";

export function RecordPage<R extends Auxiliary>({
  Form,
  list,
}: {
  Form: ComponentType<{ editing: R | null; onSaved: () => void }>;
  list: () => Promise<R[]>;
}) {
  const { data, loading, error, reload } = useData(list);
  const [editing, setEditing] = useState<R | null>(null);
  return (
    <>
      <ScreenBody>
        <Form
          key={editing?.id || "new"}
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
          data?.map((a) => (
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
