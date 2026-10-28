import "./globals.css";
import type { Metadata } from "next";
import { cookies } from "next/headers";
import type { ReactNode } from "react";

import { AUTH_TOKEN_COOKIE } from "../lib/api";
import { BrandMark } from "../components/brand-mark";
import { CommandBar } from "../components/command-bar";
import { CompareTray } from "../components/compare-tray";
import { MobileBottomNav } from "../components/mobile-bottom-nav";
import { ShellActions } from "../components/shell-actions";
import { ErrorBoundary } from "../components/error-boundary";
import { isCurrentUserAdmin } from "../lib/admin-auth";

export const metadata: Metadata = {
  title: "Intern Tracker",
  description: "Discover, track, and act on internships, hackathons, scholarships, and student opportunities."
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const cookieStore = cookies();
  const theme = cookieStore.get("intern_tracker_theme")?.value === "dark" ? "dark" : "light";
  const isAuthenticated = Boolean(cookieStore.get(AUTH_TOKEN_COOKIE)?.value);
  // only administrators should see the admin entry point
  const showAdminLink = isAuthenticated && (await isCurrentUserAdmin());

  return (
    <html lang="en" data-theme={theme}>
      <body className="bg-mist text-ink antialiased">
        <ErrorBoundary>
          {isAuthenticated && (
            <div className="page-shell pb-0 pt-5">
              <div className="mb-4 flex flex-col gap-4 rounded-full border border-white/60 bg-white/70 px-5 py-3 backdrop-blur md:flex-row md:items-center md:justify-between">
                <BrandMark compact />
                <div className="flex items-center gap-3">
                  <CommandBar />
                  <ShellActions
                    initialTheme={theme}
                    initialAuthenticated={isAuthenticated}
                    showAdminLink={showAdminLink}
                  />
                </div>
              </div>
            </div>
          )}
          {children}
          <CompareTray />
          <MobileBottomNav />
        </ErrorBoundary>
      </body>
    </html>
  );
}
