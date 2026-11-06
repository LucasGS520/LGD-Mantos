import type { ReactNode } from "react";
interface SectionProps {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  top?: number;
}
export function Section({ title, action, children, top = 18 }: SectionProps) {
  return (
    <div style={{ marginTop: top }}>
      {(title || action) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 10,
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 700,
              color: "var(--text-2)",
              letterSpacing: 0.5,
              textTransform: "uppercase",
            }}
          >
            {title}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}
