export function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="field">
      {label}
      <input
        type={type}
        value={value}
        required={required}
        min={type === "number" ? 0 : undefined}
        step={type === "number" ? ".01" : undefined}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
