interface ErrorBodyProps {
  msg: string;
  onRetry: () => void;
}
export function ErrorBody({ msg, onRetry }: ErrorBodyProps) {
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 14,
        padding: 32,
      }}
    >
      <div
        style={{
          fontSize: 13,
          color: "#F5847B",
          textAlign: "center",
          lineHeight: 1.5,
        }}
      >
        {msg}
      </div>
      <button
        onClick={onRetry}
        style={{
          padding: "8px 20px",
          borderRadius: 10,
          background: "var(--bg-2)",
          border: "1px solid var(--line-2)",
          color: "var(--text-2)",
          fontSize: 13,
          fontWeight: 600,
        }}
      >
        Tentar novamente
      </button>
    </div>
  );
}
