import { useNav } from "../../../app/nav";
import { Card } from "../../../shared/ui";
import { OperationSummary } from "../../operations";
import type { Operation } from "../../operations/contracts";
export function OperationCard({ operation }: { operation: Operation }) {
  const { navigate } = useNav();
  return (
    <Card onClick={() => navigate("operation-detail", { id: operation.id })}>
      <OperationSummary operation={operation} />
      <span>Consultar origem →</span>
    </Card>
  );
}
