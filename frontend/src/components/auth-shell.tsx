import type { ReactNode } from "react";

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto grid min-h-screen max-w-6xl grid-cols-1 lg:grid-cols-2">
        {/* Left brand panel */}
        <aside className="relative hidden overflow-hidden bg-primary text-primary-foreground lg:flex lg:flex-col lg:justify-between p-10">
          <div className="flex items-center gap-2">
            <Logo />
            <span className="font-display text-lg font-semibold">CreditIQ</span>
          </div>
          <div>
            <h2 className="font-display text-4xl leading-tight">
              A calmer way to borrow.
            </h2>
            <p className="mt-4 max-w-sm text-sm/relaxed text-primary-foreground/80">
              CreditIQ is an AI loan officer. Ask questions, apply in a
              conversation, and get a sanction letter — all without a phone tree.
            </p>
          </div>
          <div className="text-xs text-primary-foreground/60">
            Secured with bank-grade encryption.
          </div>
          <div
            aria-hidden
            className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-accent/30 blur-3xl"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-accent/20 blur-3xl"
          />
        </aside>

        {/* Right form panel */}
        <main className="flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-sm">
            <div className="mb-8 flex items-center gap-2 lg:hidden">
              <Logo />
              <span className="font-display text-lg font-semibold text-foreground">CreditIQ</span>
            </div>
            <h1 className="font-display text-3xl font-semibold text-foreground">{title}</h1>
            {subtitle && <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>}
            <div className="mt-8">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
}

function Logo() {
  return (
    <span
      aria-hidden
      className="grid h-8 w-8 place-items-center rounded-md bg-accent text-accent-foreground font-display text-sm font-bold"
    >
      C
    </span>
  );
}
