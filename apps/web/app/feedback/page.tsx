import { redirect } from "next/navigation";
import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { AppHeader } from "../../components/app-header";
import { FeedbackComposer } from "../../components/feedback-composer";
import { getServerAuthToken } from "../../lib/session";
import { siteConfig } from "../../lib/site-config";
import { isCurrentUserAdmin } from "../../lib/admin-auth";

export const dynamic = "force-dynamic";

export default async function FeedbackPage() {
  const token = await getServerAuthToken();
  if (!token) {
    redirect("/");
  }
  const showAdminLink = await isCurrentUserAdmin();

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[32px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Feedback"
          title="Collect ideas, bugs, and feature requests"
          description="A modern app should make feedback easy. This page gives users clear routes to report issues and suggest product improvements."
        />

        <div className="mt-8 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-[30px] border border-white/60 bg-white/90 p-6">
            <h2 className="text-xl font-semibold text-ink">Share feedback fast</h2>
            <div className="mt-5 grid gap-4">
              {[
                ["Bug report", "Broken route, missing data, slow load, layout issue"],
                ["Feature request", "New workflow, better filters, reminders, analytics"],
                ["General feedback", "What feels useful, confusing, or incomplete"]
              ].map(([title, copy]) => (
                <div key={title} className="rounded-[22px] bg-mist p-4">
                  <p className="font-semibold text-ink">{title}</p>
                  <p className="mt-2 text-sm text-slate">{copy}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[30px] bg-ink p-6 text-mist">
            <p className="text-xs uppercase tracking-[0.28em] text-mint/80">Preferred feedback channel</p>
            <h2 className="mt-3 text-2xl font-semibold">Send feedback directly</h2>
            <p className="mt-3 max-w-xl text-sm leading-7 text-mint/80">
              Until a database-backed feedback form is added, users can send product notes directly through email or
              reach out through your public profiles.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href={`mailto:${siteConfig.supportEmail}?subject=${encodeURIComponent(siteConfig.feedbackEmailSubject)}`}
                className="rounded-full bg-white px-5 py-3 text-sm font-medium text-ink"
              >
                Email feedback
              </a>
              <a
                href={`${siteConfig.githubUrl}/issues`}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-white/20 px-5 py-3 text-sm font-medium text-mist"
              >
                GitHub issues
              </a>
              <a
                href={siteConfig.linkedinUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-white/20 px-5 py-3 text-sm font-medium text-mist"
              >
                LinkedIn
              </a>
              <a
                href={siteConfig.githubUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-white/20 px-5 py-3 text-sm font-medium text-mist"
              >
                GitHub
              </a>
            </div>
          </section>
        </div>

        <div className="mt-8">
          <FeedbackComposer />
        </div>

        <section className="mt-8 rounded-[30px] border border-white/60 bg-white/90 p-6">
          <h2 className="text-xl font-semibold text-ink">What to build after this</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {[
              ["Feedback database", "Store submissions in Postgres and surface them in admin."],
              ["Public changelog", "Show users what shipped recently and what is coming next."],
              ["Priority voting", "Let users upvote feature ideas so roadmap decisions feel grounded."]
            ].map(([title, copy]) => (
              <div key={title} className="soft-card p-5">
                <p className="font-semibold text-ink">{title}</p>
                <p className="mt-2 text-sm leading-6 text-slate">{copy}</p>
              </div>
            ))}
          </div>
        </section>
      </section>
    </AppSidebarShell>
  );
}
