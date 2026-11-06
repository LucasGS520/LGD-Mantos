import { Card } from "../../../shared/ui";

export function Metric({
  label,
  value,
  onClick,
}: {
  label: string;
  value: string;
  onClick: () => void;
}) {
  return (
    <Card onClick={onClick}>
      <p>{label}</p>
      <strong className="metric">{value}</strong>
      <p>Ver registros →</p>
    </Card>
  );
}
