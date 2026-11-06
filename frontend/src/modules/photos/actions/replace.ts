import { api } from "../api";
import type { Photo } from "../contracts";

/** Só remove a foto anterior depois de salvar e organizar a substituta. */
export async function replacePhoto(
  productId: string,
  photo: Photo,
  file: File,
) {
  const added = await api.upload(productId, file);
  await api.organize(added.id, {
    position: photo.position,
    primary: photo.primary,
    variant_id: photo.variant_id,
    color: photo.color,
  });
  await api.remove(photo.id);
}
