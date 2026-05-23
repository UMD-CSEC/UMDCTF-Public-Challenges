import { Link } from "react-router-dom";

export function LlmDocsPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
      <h1 className="text-3xl font-bold text-white tracking-tight mb-4">
        You don't get everything you want in life.
      </h1>
      <p className="text-muted text-sm mb-10">
        The human-readable docs are right over there.
      </p>
      <Link
        to="/docs"
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-surface-2 hover:bg-surface-3 border border-border rounded-xl text-sm text-text-dim transition-colors"
      >
        Back to the normal docs
      </Link>
    </div>
  );
}
