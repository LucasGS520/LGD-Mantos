export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
    message: string,
  ) {
    super(message);
  }
}

export const errorText = (e: unknown) =>
  e instanceof Error ? e.message : "Não foi possível concluir";
