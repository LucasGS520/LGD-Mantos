import type { CSSProperties, ReactNode } from "react";
interface CardProps {
  children: ReactNode;
  style?: CSSProperties;
  padding?: number;
  onClick?: () => void;
  accent?: boolean;
}

export function Card({
  children,
  style,
  padding = 14,
  onClick,
  accent,
}: CardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "var(--bg-1)",
        border: `1px solid ${accent ? "rgba(212,168,71,0.35)" : "var(--line-1)"}`,
        borderRadius: "var(--r-lg)",
        padding,
        position: "relative",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
