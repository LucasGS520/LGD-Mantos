export function LoadingBody() {
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          border: "3px solid var(--bg-3)",
          borderTopColor: "var(--gold-500)",
          animation: "spin 0.8s linear infinite",
        }}
      />
    </div>
  );
}
