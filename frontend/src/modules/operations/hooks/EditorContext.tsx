import { createContext, useContext } from "react";
import type { useOperationEditor } from "./useOperationEditor";
export const EditorContext = createContext<ReturnType<
  typeof useOperationEditor
> | null>(null);
export function useEditor() {
  const value = useContext(EditorContext);
  if (!value) throw new Error("Editor indisponível");
  return value;
}
