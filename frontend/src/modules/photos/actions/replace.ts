import { api } from "../api";
import type { Photo } from "../contracts";

/** Backend preserva identidade/metadados e só remove o arquivo anterior após commit. */
export async function replacePhoto(
  productId: string,
  photo: Photo,
  file: File,
) {
  if (photo.product_id !== productId) throw new Error("Foto de outro produto");
  await api.replace(photo.id, file);
}
