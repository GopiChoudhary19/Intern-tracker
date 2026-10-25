import { redirect } from "next/navigation";
import Link from "next/link";

import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { ApplicationKanbanBoard } from "../../components/application-kanban-board";
import { AppHeader } from "../../components/app-header";
import { ProfileCompletionCard } from "../../components/profile-completion-card";
import { SavedSearchesPanel } from "../../components/saved-searches-panel";
import { NoApplicationsEmpty, NoSavedSearchesEmpty, LoadingError } from "../../components/empty-state";
import {
  getApplications,
  getNotifications,
  getProfile,
  getRecommendedOpportunities,
  getSavedSearches,
  getThreads
} from "../../lib/api";
import { getServerAuthToken } from "../../lib/session";
import type {
  ApplicationRecord,
  NotificationItem,
  OpportunitySummary,
  SavedSearch,
  ThreadItem,
  UserProfile
} from "../../lib/types";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const token = await getServerAuthToken();

  if (!token) {
    redirect("/");
  }

  let profile: UserProfile;
  let applications: ApplicationRecord[];
  let recommended: OpportunitySummary[];
  let notifications: NotificationItem[];
  let savedSearches: SavedSearch[];
  let threads: ThreadItem[];

  try {
    [profile, applications, recommended, notifications, savedSearches, threads] = await Promise.all([
      getProfile(token),
      getApplications(token),
      getRecommendedOpportunities(token),
      getNotifications(token),
      getSavedSearches(token),
      getThreads()
    ]);
  } catch {
    return (
      <main className="page-shell">
        <section className="glass-panel rounded-[32px] p-8 shadow-glow">
          <LoadingError
            title="The backend is not reachable yet"
            description="The backend may still be waking up, or the session may need to be refreshed. Once the API responds, this page should populate immediately."
            onRetry={() => window.location.reload()}
          />
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/" className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-mist">
              Back to landing
            </Link>
            <Link
              href="/opportunities"
              className="rounded-full border border-teal/20 px-5 py-3 text-sm font-medium text-teal"
            >
              Open feed
            </Link>
          </div>
        </section>
      </main>
    );
  }

  const savedCount = applications.filter((item) => item.status === "saved").length;
  const activeCount = applications.filter((item) => item.status !== "rejected").length;
  const showAdminLink = Boolean(process.env.INTERN_TRACKER_ADMIN_TOKEN);

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Dashboard"
          title={`Welcome back, ${profile.full_name.split(" ")[0]}`}
          description="Track momentum, review recommendations, and keep deadlines from slipping."
          links={[
            { href: "/opportunities", label: "Browse feed" },
            { href: "/profile", label: "Edit profile" }
          ]}
        />

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {[
            ["Applications", applications.length.toString()],
            ["Saved", savedCount.toString()],
            ["In play", activeCount.toString()],
            ["Recommendations", recommended.length.toString()]
          ].map(([label, value]) => (
            <div key={label} className="rounded-3xl border border-white/60 bg-white/90 p-5">
              <p className="text-sm text-slate">{label}</p>
              <p className="mt-2 text-3xl font-semibold text-ink">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="min-w-0 space-y-6">
            <section>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-ink">Application pipeline</h2>
                <Link href="/opportunities" className="text-sm font-medium text-teal">
                  Add more
                </Link>
              </div>
              {applications.length === 0 ? (
                <NoApplicationsEmpty />
              ) : (
                <ApplicationKanbanBoard items={applications} />
              )}
            </section>

            <section>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-ink">Saved searches</h2>
                <Link href="/opportunities" className="text-sm font-medium text-teal">
                  Create one
                </Link>
              </div>
              <SavedSearchesPanel items={savedSearches} />
            </section>
          </div>

          <div className="space-y-6">
            <ProfileCompletionCard profile={profile} />

            <section className="rounded-3xl bg-ink p-5 text-mist">
              <h2 className="text-lg font-semibold">Recommended for your profile</h2>
              <div className="mt-4 space-y-3">
                {recommended.map((item) => (
                  <Link key={item.id} href={`/opportunities/${item.slug}`} className="block rounded-2xl bg-white/10 p-4">
                    <p className="font-medium">{item.title}</p>
                    <p className="mt-1 text-sm text-mint">{item.organization}</p>
                  </Link>
                ))}
              </div>
            </section>

            <section className="rounded-3xl border border-white/60 bg-white/90 p-5">
              <h2 className="text-lg font-semibold text-ink">Notifications</h2>
              {notifications.length === 0 ? (
                <div className="mt-4 rounded-2xl bg-mist p-4 text-sm text-slate">
                  No urgent reminders right now. Your next alerts will appear here.
                </div>
              ) : (
                <div className="mt-4 space-y-3">
                  {notifications.map((item) => (
                    <div key={item.id} className="rounded-2xl bg-mist p-4">
                      <p className="font-medium text-ink">{item.title}</p>
                      <p className="mt-1 text-sm text-slate">{item.detail}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-3xl border border-white/60 bg-white/90 p-5">
              <h2 className="text-lg font-semibold text-ink">Community pulse</h2>
              <div className="mt-4 space-y-3">
                {threads.map((thread) => (
                  <div key={thread.id} className="rounded-2xl bg-mist p-4">
                    <p className="font-medium text-ink">{thread.title}</p>
                    <p className="mt-1 text-sm text-slate">
                      {thread.category} | {thread.author_name}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      </section>
    </AppSidebarShell>
  );
}
