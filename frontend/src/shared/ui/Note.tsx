import { type ReactNode } from "react";
export function Note({ children }: { children: ReactNode }) {
  return <p className="message">{children}</p>;
}
