export function Lost({ reason }: { reason: string }) {
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <div
        className="bg-card fade-up px-10 py-8 text-center"
        style={{
          width: "min(440px, 100%)",
          borderRadius: "6px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 6px 16px rgba(0,0,0,0.04)",
        }}
      >
        <div className="text-ask font-semibold uppercase text-[11px] tracking-wider">
          Session ended
        </div>
        <h2 className="text-[20px] font-bold text-ink mt-2">Connection closed</h2>
        <p className="text-[13px] text-ash mt-3">{reason}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 bg-teal hover:bg-teal-dark text-white text-[12px] font-semibold uppercase tracking-wider
                     px-6 py-2.5 rounded-[4px] transition-colors"
        >
          Return to portal
        </button>
      </div>
    </div>
  );
}
