import { Routes, Route, Navigate } from "react-router-dom";
import { AppProvider, useApp } from "./lib/store.tsx";
import { AuthPage } from "./pages/AuthPage.tsx";
import { MarketsPage } from "./pages/MarketsPage.tsx";
import { MarketDetailPage } from "./pages/MarketDetailPage.tsx";
import { PortfolioPage } from "./pages/PortfolioPage.tsx";
import { ApiDocsPage } from "./pages/ApiDocsPage.tsx";
import { LlmDocsPage } from "./pages/LlmDocsPage.tsx";
import { Layout } from "./components/Layout.tsx";

function RestoreGate({ children }: { children: React.ReactNode }) {
  const { restoring } = useApp();
  if (restoring) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          </svg>
          <span className="text-sm font-medium">Reconnecting...</span>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { authenticated } = useApp();
  if (!authenticated) return <Navigate to="/auth" replace />;
  return <>{children}</>;
}

function AuthRoute({ children }: { children: React.ReactNode }) {
  const { authenticated } = useApp();
  if (authenticated) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <RestoreGate>
      <Routes>
        <Route
          path="/auth"
          element={
            <AuthRoute>
              <AuthPage />
            </AuthRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<MarketsPage />} />
          <Route path="market/:id" element={<MarketDetailPage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="docs" element={<ApiDocsPage />} />
          <Route path="docs/llms" element={<LlmDocsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </RestoreGate>
  );
}

export function App() {
  return (
    <AppProvider>
      <AppRoutes />
    </AppProvider>
  );
}
