import { type ReactNode } from "react";
export function Options({ children }: { children: ReactNode }) {
  return <div className="actions">{children}</div>;
}
