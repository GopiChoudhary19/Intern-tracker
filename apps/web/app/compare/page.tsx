import { redirect } from "next/navigation";
import Link from "next/link";

import { AppSidebarShell } from "../../components/app-sidebar-shell";
import { AppHeader } from "../../components/app-header";
import { getOpportunity } from "../../lib/api";
import { getServerAuthToken } from "../../lib/session";
import type { OpportunityDetail } from "../../lib/types";
import { isCurrentUserAdmin } from "../../lib/admin-auth";

export const dynamic = "force-dynamic";

type ComparePageProps = {
  searchParams?: {
    slugs?: string;
  };
};

function stipendLabel(item: OpportunityDetail) {
  if (item.stipend_min == null && item.stipend_max == null) return "Not specified";
  return `${item.currency ?? "INR"} ${item.stipend_min ?? 0} - ${item.stipend_max ?? 0}`;
}

// Type predicate for filtering non-null values
function isNotNull<T>(value: T | null): value is T {
  return value !== null;
}

export default async function ComparePage({ searchParams }: ComparePageProps) {
  const token = await getServerAuthToken();
  if (!token) {
    redirect("/");
  }
  const showAdminLink = await isCurrentUserAdmin();
  
  const slugs = (searchParams?.slugs ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is string => Boolean(item))
    .slice(0, 3);

  const items = (
    await Promise.all(
      slugs.map(async (slug) => {
        try {
          return await getOpportunity(slug);
        } catch {
          return null;
        }
      })
    )
  ).filter(isNotNull);

  return (
    <AppSidebarShell isAuthenticated={Boolean(token)} showAdminLink={showAdminLink}>
      <section className="glass-panel rounded-[34px] p-6 shadow-glow md:p-8">
        <AppHeader
          eyebrow="Compare"
          title="Opportunity comparison"
          description="Review compensation, skills, eligibility, and deadlines side by side before you commit."
          links={[{ href: "/opportunities", label: "Back to feed" }]}
        />

        {items.length === 0 ? (
          <div className="mt-8 rounded-3xl border border-teal/10 bg-white/90 p-6 text-sm text-slate">
            Add opportunities to compare from the feed or detail pages first.
          </div>
        ) : (
          <div className="mt-8 grid gap-5 lg:grid-cols-3">
            {items.map((item) => (
              <article key={item.id} className="rounded-[28px] border border-white/60 bg-white/90 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-semibold text-ink">{item.title}</h2>
                    <p className="mt-1 text-sm text-slate">{item.organization}</p>
                  </div>
                  <span className="rounded-full bg-teal/10 px-3 py-1 text-xs text-teal">{item.type}</span>
                </div>
                <div className="mt-5 space-y-3 text-sm text-slate">
                  <p><span className="font-medium text-ink">Mode:</span> {item.mode}</p>
                  <p><span className="font-medium text-ink">Domain:</span> {item.domain}</p>
                  <p><span className="font-medium text-ink">Compensation:</span> {stipendLabel(item)}</p>
                  <p><span className="font-medium text-ink">Eligibility:</span> {item.eligibility_text ?? "Check listing"}</p>
                  <div>
                    <p className="font-medium text-ink">Skills</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {item.required_skills.map((skill) => (
                        <span key={skill} className="rounded-full bg-mist px-3 py-1 text-xs text-slate">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <Link href={`/opportunities/${item.slug}`} className="mt-5 inline-flex text-sm font-medium text-teal">
                  Open detail
                </Link>
              </article>
            ))}
          </div>
        )}
      </section>
    </AppSidebarShell>
  );
}
