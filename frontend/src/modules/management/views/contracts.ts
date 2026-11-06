import type { ReactNode } from "react";
import type { useNav } from "../../../app/nav";
import type { Auxiliary } from "../../auxiliaries/contracts";
import type { Operation } from "../../operations/contracts";
import type { Group, Report } from "../contracts";
export interface ViewProps {
  data: Report;
  setView: (value: string) => void;
  navigate: ReturnType<typeof useNav>["navigate"];
  sort: string;
  setSort: (value: string) => void;
  sources: (ids: string[]) => ReactNode;
  attribute: string;
  setAttribute: (value: string) => void;
  groups: (rows: Group[]) => ReactNode;
  opLink: (operation: Operation) => ReactNode;
  supplier: string;
  setSupplier: (value: string) => void;
  suppliers: Auxiliary[];
}
