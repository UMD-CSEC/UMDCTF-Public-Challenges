export function Intro({ onStart, connecting }: { onStart: () => void; connecting: boolean }) {
  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      {/* Top bar — dated branding */}
      <header className="bg-white border-b border-rule px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-1">
          <img src="/logo.png" alt="" className="w-8 h-8 object-contain" />
          <div className="flex items-baseline gap-2">
            <span
              className="font-bold italic text-teal text-[22px] tracking-tight"
              style={{ fontFamily: "'Open Sans', sans-serif" }}
            >
              Choppediver
            </span>
            <span className="text-ash text-[12px] tracking-wide uppercase">Assessment Portal</span>
          </div>
        </div>
        <div className="text-ash text-[12px]">
          Candidate ID&nbsp;·&nbsp;{Math.floor(10000 + Math.random() * 90000)}
        </div>
      </header>

      {/* Main card */}
      <main className="flex-1 flex items-center justify-center px-4">
        <div
          className="bg-card fade-up"
          style={{
            width: "min(560px, 100%)",
            borderRadius: "6px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 6px 16px rgba(0,0,0,0.04)",
          }}
        >
          <div className="px-10 pt-10 pb-8">
            <h1 className="text-[26px] font-bold text-ink mb-2">Welcome, candidate.</h1>
            <p className="text-[14px] text-ash leading-[1.6] mb-4">
              At Choppediver, the people who excel are the ones who can react
              quickly in fast-paced environments. This assessment is designed
              to measure exactly that.
            </p>
            <p className="text-[14px] text-ash leading-[1.6] mb-8">
              Please ensure you have a stable internet connection and a quiet
              environment before continuing. The assessment must be completed
              in one session.
            </p>

            <dl className="text-[13px] border-t border-rule pt-5 space-y-3 mb-8">
              <Row k="Role">Software Engineer Intern</Row>
              <Row k="Section">Directional Forecasting</Row>
              <Row k="Expected duration">~5 min</Row>
            </dl>

            <button
              onClick={onStart}
              disabled={connecting}
              className="w-full bg-teal hover:bg-teal-dark text-white text-[14px] font-semibold tracking-wide uppercase
                         py-3 rounded-[4px] transition-colors
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {connecting ? "Connecting…" : "Begin Assessment"}
            </button>
          </div>
        </div>
      </main>

      <footer className="border-t border-rule bg-white py-3 px-8 text-[11px] text-ash flex items-center justify-between">
        <span>© 2012–2026 Choppediver Securities, LLC. All rights reserved.</span>
        <span>Portal v1.8.6</span>
      </footer>
    </div>
  );
}

function Row({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-ash">{k}</dt>
      <dd className="text-ink font-medium">{children}</dd>
    </div>
  );
}
