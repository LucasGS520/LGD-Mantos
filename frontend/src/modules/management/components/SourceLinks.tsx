import { useNav } from "../../../app/nav";
import { useState } from "react";
import { Button } from "../../../shared/ui/Button";
import { Options } from "../../../shared/ui/Options";
export function SourceLinks({ ids }: { ids: string[] }) {
  const { navigate } = useNav();
  const [shown, setShown] = useState(10);
  return (
    <Options>
      {ids.slice(0, shown).map((id) => (
        <Button key={id} onClick={() => navigate("operation-detail", { id })}>
          Registro {id.slice(0, 8)}
        </Button>
      ))}
      {shown < ids.length && (
        <Button onClick={() => setShown(shown + 10)}>
          Ver mais origens ({ids.length - shown})
        </Button>
      )}
    </Options>
  );
}
