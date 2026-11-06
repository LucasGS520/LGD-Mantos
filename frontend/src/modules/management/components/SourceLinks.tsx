import { useNav } from "../../../app/nav";
import { Button } from "../../../shared/ui/Button";
import { Options } from "../../../shared/ui/Options";
export function SourceLinks({ ids }: { ids: string[] }) {
  const { navigate } = useNav();
  return (
    <Options>
      {ids.map((id) => (
        <Button key={id} onClick={() => navigate("operation-detail", { id })}>
          Registro {id.slice(0, 8)}
        </Button>
      ))}
    </Options>
  );
}
