import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedLayout,
  ssr: false,
});

function AuthenticatedLayout() {
  const { token, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !token) navigate({ to: "/login", replace: true });
  }, [token, loading, navigate]);

  if (loading || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground animate-shimmer-pulse">Loading…</div>
      </div>
    );
  }
  return <Outlet />;
}
