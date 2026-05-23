import { useState, useCallback } from "react";
import { useApp } from "../lib/store.tsx";

export function AuthPage() {
  const { connectAndLogin, connectAndRegister, disconnectReason } = useApp();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(disconnectReason || "");
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError("");
      setLoading(true);

      try {
        if (mode === "login") {
          await connectAndLogin(username, password);
        } else {
          await connectAndRegister(username, password);
        }
      } catch (err: any) {
        setError(err.message || "Connection failed");
      } finally {
        setLoading(false);
      }
    },
    [mode, username, password, connectAndLogin, connectAndRegister],
  );

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      {/* Background grid */}
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(var(--color-border) 1px, transparent 1px),
                           linear-gradient(90deg, var(--color-border) 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      />

      <div className="relative w-full max-w-md animate-slide-up">
        {/* Logo / brand */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                <polyline points="16 7 22 7 22 13" />
              </svg>
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">
              UMDMarket
            </span>
          </div>
          <p className="text-muted text-sm">
            Trade prediction markets. Find the edge.
          </p>
        </div>

        {/* Card */}
        <div className="bg-surface-2 border border-border rounded-2xl p-8 shadow-2xl shadow-black/40">
          {/* Tabs */}
          <div className="flex gap-1 p-1 bg-surface rounded-xl mb-8">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError("");
              }}
              className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 ${
                mode === "login"
                  ? "bg-surface-3 text-white shadow-sm"
                  : "text-muted hover:text-text-dim"
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setError("");
              }}
              className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 ${
                mode === "register"
                  ? "bg-surface-3 text-white shadow-sm"
                  : "text-muted hover:text-text-dim"
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-muted uppercase tracking-wider mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="8+ alphanumeric characters"
                className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-white placeholder:text-muted/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-mono text-sm"
                required
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-muted uppercase tracking-wider mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={
                  mode === "register" ? "12+ chars, mixed case, digit, symbol" : "Enter password"
                }
                className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-white placeholder:text-muted/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all font-mono text-sm"
                required
                minLength={mode === "register" ? 12 : 1}
              />
            </div>

            {error && (
              <div className="px-4 py-3 bg-no-dim border border-no/20 rounded-xl text-no text-sm font-medium animate-fade-in">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-primary/20 hover:shadow-primary/30 active:scale-[0.98]"
            >
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg
                    className="animate-spin h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="3"
                      className="opacity-25"
                    />
                    <path
                      d="M4 12a8 8 0 018-8"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  </svg>
                  Connecting...
                </span>
              ) : mode === "login" ? (
                "Sign In"
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          {mode === "register" && (
            <div className="mt-6 pt-5 border-t border-border">
              <p className="text-xs text-muted leading-relaxed">
                <span className="text-text-dim font-medium">
                  Password requirements:
                </span>{" "}
                12+ characters with uppercase, lowercase, digit, and special
                character.
              </p>
            </div>
          )}
        </div>

        {/* Starting balance note */}
        <p className="text-center text-xs text-muted mt-6">
          New accounts start with{" "}
          <span className="text-yes font-mono font-semibold">$100.00</span>{" "}
          balance
        </p>
      </div>
    </div>
  );
}
