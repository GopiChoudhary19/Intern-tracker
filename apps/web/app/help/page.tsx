import { redirect } from "next/navigation";
import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { AppHeader } from "../../components/app-header";
import { getServerAuthToken } from "../../lib/session";
import { siteConfig } from "../../lib/site-config";
import { isCurrentUserAdmin } from "../../lib/admin-auth";

export const dynamic = "force-dynamic";

export default async function HelpPage() {
  const token = await getServerAuthToken();
  if (!token) {
    redirect("/");
  }
  const showAdminLink = await isCurrentUserAdmin();

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Help"
          title="Help center and direct contact"
          description="Give users a clear place to get support, report issues, and reach you without hunting through the app."
        />

        <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-[30px] bg-ink p-6 text-mist">
            <p className="text-xs uppercase tracking-[0.28em] text-mint/80">Connect with me</p>
            <div className="mt-5 space-y-4">
              <a
                href={`mailto:${siteConfig.supportEmail}`}
                className="block rounded-[22px] bg-white/10 p-4 transition hover:bg-white/15"
              >
                <p className="text-lg font-semibold">Email</p>
                <p className="mt-1 text-sm text-mint/80">{siteConfig.supportEmail}</p>
              </a>
              <a
                href={siteConfig.linkedinUrl}
                target="_blank"
                rel="noreferrer"
                className="block rounded-[22px] bg-white/10 p-4 transition hover:bg-white/15"
              >
                <p className="text-lg font-semibold">LinkedIn</p>
                <p className="mt-1 text-sm text-mint/80">{siteConfig.linkedinUrl}</p>
              </a>
              <a
                href={siteConfig.githubUrl}
                target="_blank"
                rel="noreferrer"
                className="block rounded-[22px] bg-white/10 p-4 transition hover:bg-white/15"
              >
                <p className="text-lg font-semibold">GitHub</p>
                <p className="mt-1 text-sm text-mint/80">{siteConfig.githubUrl}</p>
              </a>
            </div>
          </section>

          <section className="rounded-[30px] border border-white/60 bg-white/90 p-6">
            <h2 className="text-xl font-semibold text-ink">Recommended features to add next</h2>
            <div className="mt-5 grid gap-4">
              {[
                [
                  "Saved searches and alerts",
                  "Let users follow keywords and get notified when matching internships or hackathons appear."
                ],
                [
                  "Resume match score",
                  "Show how strongly each profile fits an opportunity with missing-skill hints."
                ],
                [
                  "Deadline calendar sync",
                  "Push saved deadlines and follow-ups into Google Calendar so students do not miss them."
                ],
                [
                  "Submission feedback inbox",
                  "Collect bug reports, suggestions, and feature requests from inside the product."
                ]
              ].map(([title, copy]) => (
                <div key={title} className="rounded-[22px] bg-mist p-4">
                  <p className="font-semibold text-ink">{title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate">{copy}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="mt-8 rounded-[30px] border border-white/60 bg-white/90 p-6">
          <h2 className="text-xl font-semibold text-ink">Support topics</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {[
              ["Account access", "Use email or phone OTP on the landing page, then revisit dashboard or profile."],
              ["Admin access", "If `/admin` is missing on the live site, the Render web service needs a fresh deploy."],
              ["Data issues", "If opportunities or profiles do not load, verify the API service and environment values."]
            ].map(([title, copy]) => (
              <div key={title} className="soft-card p-5">
                <p className="font-semibold text-ink">{title}</p>
                <p className="mt-2 text-sm leading-6 text-slate">{copy}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-[30px] border border-white/60 bg-white/90 p-6">
          <h2 className="text-xl font-semibold text-ink">Fast support actions</h2>
          <div className="mt-5 flex flex-wrap gap-3">
            <a
              href={`mailto:${siteConfig.supportEmail}?subject=${encodeURIComponent("Intern Radar help request")}`}
              className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-mist"
            >
              Email me
            </a>
            <a
              href={siteConfig.linkedinUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-teal/20 bg-white px-5 py-3 text-sm font-medium text-teal"
            >
              Connect on LinkedIn
            </a>
            <a
              href={siteConfig.githubUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-teal/20 bg-white px-5 py-3 text-sm font-medium text-teal"
            >
              Open GitHub
            </a>
          </div>
        </section>
      </section>
    </AppSidebarShell>
  );
}
