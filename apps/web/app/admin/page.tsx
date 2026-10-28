import { redirect } from "next/navigation";
import Link from "next/link";

import { AdminFeedbackTriage } from "../../components/admin-feedback-triage";
import { AdminOpportunityManager } from "../../components/admin-opportunity-manager";
import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { AppHeader } from "../../components/app-header";
import { getAdminFeedback, getAdminOpportunities, getAdminOverview, getAdminUsers } from "../../lib/admin";
import { isCurrentUserAdmin } from "../../lib/admin-auth";
import { getServerAuthToken } from "../../lib/session";
import type { AdminFeedbackItem, AdminUserSummary, AnalyticsOverview, OpportunityDetail } from "../../lib/types";

export const dynamic = "force-dynamic";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric"
  }).format(new Date(value));
}

export default async function AdminPage() {
  const token = await getServerAuthToken();
  if (!token) {
    redirect("/");
  }
  // being signed in is not enough: this page lists every user's contact details
  if (!(await isCurrentUserAdmin())) {
    redirect("/dashboard");
  }
  const adminTokenConfigured = Boolean(process.env.INTERN_TRACKER_ADMIN_TOKEN);

  // SECURITY: Redirect unauthenticated users from admin page
  if (!adminTokenConfigured) {
    return (
      <main className="page-shell">
        <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
          <AppHeader
            eyebrow="Admin"
            title="Admin access is not configured."
            description="The administrator token is not set in the environment variables. Only users with proper admin token can access this page."
            links={[
              { href: "/", label: "Landing" },
              { href: "/dashboard", label: "Dashboard" }
            ]}
          />
          <div className="mt-8 rounded-[28px] border border-coral/20 bg-white/90 p-6 text-sm leading-7 text-slate">
            <strong>Setup Instructions:</strong> Set `INTERN_TRACKER_ADMIN_TOKEN` environment variable on both the API service and web service in Render, then redeploy both.
          </div>
        </section>
      </main>
    );
  }

  let overview: AnalyticsOverview;
  let users: AdminUserSummary[];
  let feedbackItems: AdminFeedbackItem[];
  let opportunities: OpportunityDetail[];

  try {
    [overview, { items: users }, { items: feedbackItems }, { items: opportunities }] = await Promise.all([
      getAdminOverview(),
      getAdminUsers(),
      getAdminFeedback(),
      getAdminOpportunities()
    ]);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Admin data is unavailable.";
    return (
      <main className="page-shell">
        <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
          <AppHeader
            eyebrow="Admin"
            title="Admin access denied."
            description={message}
            links={[
              { href: "/", label: "Landing" },
              { href: "/dashboard", label: "Dashboard" }
            ]}
          />
          <div className="mt-8 rounded-[28px] border border-coral/20 bg-white/90 p-6 text-sm leading-7 text-slate">
            <strong>Note:</strong> Admin access requires a valid `X-Admin-Token` header. This endpoint is protected and will reject requests without proper authentication.
          </div>
        </section>
      </main>
    );
  }

  const showAdminLink = true;
  const completedUsers = users.filter((user) => user.onboarding_completed).length;
  const incompleteUsers = users.length - completedUsers;
  const recentUsers = users.slice(0, 4);
  const recentFeedback = feedbackItems.slice(0, 8);

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Admin"
          title="Platform command center"
          description="Monitor student activity, review onboarding health, and keep the discovery pipeline moving from one modern control room."
          links={[
            { href: "/dashboard", label: "Dashboard" },
            { href: "/opportunities", label: "Feed" }
          ]}
        />

        <div className="mt-8 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-[30px] bg-ink p-6 text-mist">
            <p className="text-xs uppercase tracking-[0.28em] text-mint/75">Live snapshot</p>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {[
                ["Active users", overview.active_users.toString()],
                ["Live opportunities", overview.new_opportunities.toString()],
                ["Saved applications", overview.saved_applications.toString()],
                ["Applied applications", overview.applied_applications.toString()]
              ].map(([label, value]) => (
                <div key={label} className="rounded-[24px] bg-white/10 p-5">
                  <p className="text-sm text-mint/80">{label}</p>
                  <p className="mt-3 text-4xl font-semibold text-white">{value}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[30px] border border-white/60 bg-white/90 p-6">
            <p className="text-xs uppercase tracking-[0.28em] text-teal">Health checks</p>
            <div className="mt-5 space-y-4">
              <div className="rounded-[22px] bg-mist p-4">
                <p className="text-sm text-slate">Completed onboarding</p>
                <p className="mt-2 text-2xl font-semibold text-ink">{completedUsers}</p>
              </div>
              <div className="rounded-[22px] bg-mist p-4">
                <p className="text-sm text-slate">Needs onboarding follow-up</p>
                <p className="mt-2 text-2xl font-semibold text-ink">{incompleteUsers}</p>
              </div>
              <div className="rounded-[22px] border border-dashed border-teal/20 bg-white p-4 text-sm leading-6 text-slate">
                API shortcut: <code>GET /api/v1/admin/users</code> with the <code>X-Admin-Token</code> header.
              </div>
            </div>
          </section>
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
          <section className="rounded-[30px] border border-white/60 bg-white/90 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-ink">Recent user activity</h2>
                <p className="mt-1 text-sm text-slate">Newest accounts and profile completion status.</p>
              </div>
              <p className="text-sm text-slate">{users.length} total users</p>
            </div>

            <div className="mt-5 space-y-3">
              {recentUsers.map((user) => (
                <div key={user.id} className="rounded-[24px] bg-mist p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-ink">{user.full_name}</p>
                      <p className="mt-1 text-sm text-slate">{user.email ?? user.phone ?? "No contact info"}</p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-teal">
                      {user.onboarding_completed ? "Complete" : "Pending"}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate">
                    {[user.college_name, user.degree, user.branch].filter(Boolean).join(" | ") || "Academics pending"}
                  </p>
                  <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate">
                    Joined {formatDate(user.created_at)}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[30px] border border-white/60 bg-white/90 p-6">
            <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-ink">User directory</h2>
                <p className="mt-1 text-sm leading-6 text-slate">
                  Review profile quality, contact coverage, location data, and application counts in one place.
                </p>
              </div>
              <Link href="/profile" className="text-sm font-medium text-teal">
                Check profile schema
              </Link>
            </div>

            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-y-3 text-left text-sm">
                <thead>
                  <tr className="text-slate">
                    <th className="px-3 py-2 font-medium">User</th>
                    <th className="px-3 py-2 font-medium">Contact</th>
                    <th className="px-3 py-2 font-medium">Academics</th>
                    <th className="px-3 py-2 font-medium">Location</th>
                    <th className="px-3 py-2 font-medium">Tracker</th>
                    <th className="px-3 py-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="rounded-2xl bg-mist text-ink">
                      <td className="rounded-l-2xl px-3 py-4 align-top">
                        <div className="font-medium">{user.full_name}</div>
                        <div className="mt-1 text-xs text-slate">{user.id}</div>
                      </td>
                      <td className="px-3 py-4 align-top text-slate">
                        <div>{user.email ?? "No email"}</div>
                        <div className="mt-1">{user.phone ?? "No phone"}</div>
                      </td>
                      <td className="px-3 py-4 align-top text-slate">
                        <div>{user.college_name ?? "No college"}</div>
                        <div className="mt-1">
                          {[user.degree, user.branch, user.graduation_year?.toString()].filter(Boolean).join(" | ") ||
                            "Not completed"}
                        </div>
                      </td>
                      <td className="px-3 py-4 align-top text-slate">
                        {[user.city, user.country].filter(Boolean).join(", ") || "Not provided"}
                      </td>
                      <td className="px-3 py-4 align-top text-slate">
                        <div>{user.applications_count} applications</div>
                        <div className="mt-1">
                          {user.onboarding_completed ? "Onboarding complete" : "Onboarding incomplete"}
                        </div>
                      </td>
                      <td className="rounded-r-2xl px-3 py-4 align-top text-slate">{formatDate(user.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <section className="mt-8 rounded-[30px] border border-white/60 bg-white/90 p-6">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-ink">Feedback inbox</h2>
              <p className="mt-1 text-sm leading-6 text-slate">
                User-reported bugs, product requests, and general feedback submitted from inside the app.
              </p>
            </div>
            <p className="text-sm text-slate">{feedbackItems.length} submissions</p>
          </div>

          <AdminFeedbackTriage items={recentFeedback} />
        </section>

        <div className="mt-8">
          <AdminOpportunityManager opportunities={opportunities} />
        </div>
      </section>
    </AppSidebarShell>
  );
}
