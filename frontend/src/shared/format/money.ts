import type { Money } from "../api/contracts";
export const brl = (value: Money | number | undefined) =>
  value === null || value === undefined
    ? "Não informado"
    : Number(value).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
      });
