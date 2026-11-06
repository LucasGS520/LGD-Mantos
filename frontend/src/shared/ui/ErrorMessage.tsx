export function ErrorMessage({ message }: { message: string | null }) {
  return message ? (
    <p role="alert" className="message danger">
      {message}
    </p>
  ) : null;
}
