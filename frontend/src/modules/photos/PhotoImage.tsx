import { useEffect, useState } from "react";
import { errorText } from "../../shared/api/errors";
import { api } from "./api";
export function PhotoImage({ id }: { id: string }) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    let objectUrl = "";
    api
      .photo(id)
      .then((value) => {
        objectUrl = value;
        if (alive) setUrl(value);
        else URL.revokeObjectURL(value);
      })
      .catch((e) => {
        if (alive) setError(errorText(e));
      });
    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [id]);
  return url ? (
    <img className="photo" src={url} alt="Foto do produto" />
  ) : (
    <p>{error || "Carregando foto…"}</p>
  );
}
