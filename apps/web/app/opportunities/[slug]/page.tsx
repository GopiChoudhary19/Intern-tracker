import { redirect } from "next/navigation";
import Link from "next/link";

import { AppSidebarShell } from "../../../components/app-sidebar-shell";
import { AppHeader } from "../../../components/app-header";
import { CompareToggleButton } from "../../../components/compare-toggle-button";
import { OpportunityActionPanel } from "../../../components/opportunity-action-panel";
import { ResumeMatchCard } from "../../../components/resume-match-card";
import { getApplications, getOpportunity, getProfile } from "../../../lib/api";
import { getServerAuthToken } from "../../../lib/session";
import type { OpportunityDetail, UserProfile } from "../../../lib/types";
import { isCurrentUserAdmin } from "../../../lib/admin-auth";

export const dynamic = "force-dynamic";

type OpportunityDetailPageProps = {
  params: {
    slug: string;
  };
};

function moneyLabel(min: number | null, max: number | null, currency: string | null) {
  if (min == null && max == null) return "Not specified";
  const formatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
  return `${currency ?? "INR"} ${formatter.format(min ?? 0)} - ${formatter.format(max ?? 0)}`;
}

export default async function OpportunityDetailPage({ params }: OpportunityDetailPageProps) {
  const token = await getServerAuthToken();
  const showAdminLink = await isCurrentUserAdmin();
  
  let opportunity: OpportunityDetail;
  try {
    opportunity = await getOpportunity(params.slug);
  } catch {
    return (
      <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
        <section className="glass-panel rounded-[34px] p-8 shadow-glow">
          <p className="text-xs uppercase tracking-[0.24em] text-teal">Opportunity Detail</p>
          <h1 className="mt-3 text-3xl font-semibold text-ink">This opportunity is unavailable right now.</h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate">
            The backend may still be starting, or this listing is temporarily unavailable.
          </p>
          <div className="mt-6">
            <Link href="/opportunities" className="rounded-full bg-ink px-5 py-3 text-sm font-medium text-mist">
              Back to feed
            </Link>
          </div>
        </section>
      </AppSidebarShell>
    );
  }
  
  const profile: UserProfile | null = token ? await getProfile(token).catch(() => null) : null;
  const applications = token ? await getApplications(token).catch(() => []) : [];
  const existingApplication = applications.find((item) => item.opportunity.id === opportunity.id);

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[34px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow={`${opportunity.type} | ${opportunity.domain} | ${opportunity.mode}`}
          title={opportunity.title}
          description={`${opportunity.organization} | ${opportunity.location_text ?? "Location flexible"}`}
          links={[{ href: "/opportunities", label: "Back to feed" }]}
        />

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-white/60 bg-white/90 p-6">
            <h2 className="text-lg font-semibold text-ink">About the role</h2>
            <p className="mt-4 text-sm leading-8 text-slate">{opportunity.description}</p>

            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-ink">Eligibility</p>
                <p className="mt-2 text-sm leading-7 text-slate">
                  {opportunity.eligibility_text ?? "Check the application link for full eligibility details."}
                </p>
              </div>
              <div>
                <p className="text-sm font-semibold text-ink">Compensation</p>
                <p className="mt-2 text-sm leading-7 text-slate">
                  {moneyLabel(opportunity.stipend_min, opportunity.stipend_max, opportunity.currency)}
                </p>
              </div>
            </div>

            <div className="mt-6">
              <p className="text-sm font-semibold text-ink">Required skills</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {opportunity.required_skills.map((skill) => (
                  <span key={skill} className="rounded-full bg-teal/10 px-3 py-1 text-xs text-teal">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="grid gap-5">
            <ResumeMatchCard profile={profile} opportunity={opportunity} />
            <OpportunityActionPanel opportunityId={opportunity.id} existingApplication={existingApplication} />
            <div className="rounded-3xl border border-teal/15 bg-white/90 p-5">
              <h3 className="text-lg font-semibold text-ink">Compare this role</h3>
              <p className="mt-2 text-sm leading-6 text-slate">
                Add this opportunity to your comparison tray and review it side by side with up to two others.
              </p>
              <div className="mt-4">
                <CompareToggleButton slug={opportunity.slug} />
              </div>
            </div>
            <div className="rounded-3xl border border-teal/15 bg-white/90 p-5">
              <h3 className="text-lg font-semibold text-ink">Application link</h3>
              <p className="mt-2 text-sm leading-6 text-slate">
                When you are ready, use the official listing and then update your tracker here.
              </p>
              <a
                href={opportunity.application_url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex rounded-full bg-coral px-5 py-2.5 text-sm font-medium text-white"
              >
                Open Official Listing
              </a>
            </div>
          </div>
        </div>
      </section>
    </AppSidebarShell>
  );
}
