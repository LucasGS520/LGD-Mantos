import { flows } from "../flows";
import { useEditor } from "../hooks/EditorContext";
export function OperationFields() {
  const { kind } = useEditor();
  const Fields = flows[kind].Fields;
  return <Fields />;
}
