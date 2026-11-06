export interface Auxiliary {
  id: string;
  kind: string;
  name: string;
  notes: string | null;
  active: boolean;
  version: number;
}

export interface RecordValues {
  name: string;
  notes: string | null;
  active: boolean;
  version?: number;
  reason?: string;
}
