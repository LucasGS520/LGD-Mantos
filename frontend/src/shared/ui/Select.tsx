export function Select({
  label,
  value,
  onChange,
  options,
  required = false,
  allowEmpty = true,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { id: string; name: string }[];
  required?: boolean;
  allowEmpty?: boolean;
}) {
  return (
    <label className="field">
      {label}
      <select
        aria-label={label}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
      >
        {allowEmpty && <option value="">Selecione</option>}
        {options.map((o) => (
          <option key={o.id} value={o.id}>
            {o.name}
          </option>
        ))}
      </select>
    </label>
  );
}
