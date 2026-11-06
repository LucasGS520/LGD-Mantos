export interface Photo {
  id: string;
  product_id: string;
  position: number;
  primary: boolean;
  variant_id: string | null;
  color: string | null;
}

export type PhotoInput = Pick<
  Photo,
  "position" | "primary" | "variant_id" | "color"
>;
