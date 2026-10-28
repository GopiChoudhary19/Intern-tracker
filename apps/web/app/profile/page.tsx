import { redirect } from "next/navigation";
import Link from "next/link";

import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { AppHeader } from "../../components/app-header";
import { ProfileForm } from "../../components/profile-form";
import { getProfile } from "../../lib/api";
import { getServerAuthToken } from "../../lib/session";
import type { UserProfile } from "../../lib/types";
import { isCurrentUserAdmin } from "../../lib/admin-auth";

export const dynamic = "force-dynamic";

export default async function ProfilePage() {
  const token = await getServerAuthToken();

  if (!token) {
    redirect("/");
  }

  let profile: UserProfile;
  try {
    profile = await getProfile(token);
  } catch {
    return (
      <main className="page-shell">
        <section className="glass-panel rounded-[32px] p-8 shadow-glow">
          <p className="text-xs uppercase tracking-[0.3em] text-teal">Profile</p>
          <h1 className="mt-3 text-3xl font-semibold text-ink">Profile data could not load.</h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate">
            The API did not return profile data yet. Refresh once the backend is healthy and your session should load.
          </p>
          <div className="mt-6">
            <Link href="/dashboard" className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-mist">
              Back to dashboard
            </Link>
          </div>
        </section>
      </main>
    );
  }

  const showAdminLink = await isCurrentUserAdmin();

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Profile"
          title="Tune your recommendations."
          description="Update domains, locations, opportunity types, and skills. Recommendations, reminders, and tracker workflows react to these preferences."
          links={[{ href: "/dashboard", label: "Back to dashboard" }]}
        />

        <div className="mt-8 rounded-[30px] border border-white/60 bg-white/90 p-6">
          <ProfileForm profile={profile} />
        </div>
      </section>
    </AppSidebarShell>
  );
}
