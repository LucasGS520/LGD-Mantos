export interface Revision {
  id: string;
  action: string;
  reason: string;
  created_at: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
}
