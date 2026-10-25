"use client";

import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { clientJsonFetch } from "../lib/client-json";
import type { ApplicationRecord } from "../lib/types";
import { ConfirmationModal } from "./ui/confirmation-modal";

const columns = [
  { id: "saved", label: "Saved", accent: "bg-sky-100 text-sky-800" },
  { id: "applied", label: "Applied", accent: "bg-amber-100 text-amber-800" },
  { id: "shortlisted", label: "Interview", accent: "bg-violet-100 text-violet-800" },
  { id: "accepted", label: "Offer", accent: "bg-emerald-100 text-emerald-800" },
  { id: "rejected", label: "Closed", accent: "bg-rose-100 text-rose-800" }
] as const;

type ColumnId = (typeof columns)[number]["id"];

type DraftState = Record<
  string,
  {
    note: string;
    next_follow_up_at: string;
  }
>;

function buildDrafts(items: ApplicationRecord[]): DraftState {
  return Object.fromEntries(
    items.map((item) => [
      item.id,
      {
        note: item.note ?? "",
        next_follow_up_at: item.next_follow_up_at ? item.next_follow_up_at.slice(0, 10) : ""
      }
    ])
  );
}

function formatDate(value: string | null) {
  if (!value) return "No deadline";
  return new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short" }).format(new Date(value));
}

export function ApplicationKanbanBoard({ items }: { items: ApplicationRecord[] }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<DraftState>(() => buildDrafts(items));
  const [isPending, startTransition] = useTransition();
  const [itemToDelete, setItemToDelete] = useState<string | null>(null);

  useEffect(() => {
    setDrafts(buildDrafts(items));
  }, [items]);

  const grouped = columns.map((column) => ({
    ...column,
    items: items.filter((item) => item.status === column.id)
  }));

  const patchApplication = (applicationId: string, payload: { status?: ColumnId; note?: string; next_follow_up_at?: string | null }) => {
    // Validate status if provided
    if (payload.status && !columns.some(col => col.id === payload.status)) {
      setMessage("Invalid status. Please refresh and try again.");
      return;
    }
    
    startTransition(async () => {
      try {
        await clientJsonFetch<ApplicationRecord>(`/api/applications/${applicationId}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });
        setMessage("Tracker updated.");
        router.refresh();
      } catch {
        setMessage("Could not update the tracker.");
      }
    });
  };

  const removeItem = () => {
    if (!itemToDelete) return;

    startTransition(async () => {
      try {
        await clientJsonFetch<{ message: string }>(`/api/applications/${itemToDelete}`, {
          method: "DELETE"
        });
        setMessage("Application removed from tracker.");
        setItemToDelete(null);
        router.refresh();
      } catch {
        setMessage("Could not remove that item.");
      }
    });
  };

  return (
    <div>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {grouped.map((column) => (
          <section key={column.id} className="w-64 shrink-0 rounded-[28px] border border-white/60 bg-white/85 p-4 shadow-glow">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-ink">{column.label}</h3>
              <span className={`rounded-full px-3 py-1 text-xs font-medium ${column.accent}`}>{column.items.length}</span>
            </div>

            <div className="mt-4 space-y-4">
              {column.items.length === 0 ? (
                <div className="rounded-[22px] border border-dashed border-teal/15 bg-mist/70 p-4 text-sm text-slate">
                  No applications here yet.
                </div>
              ) : (
                column.items.map((item, index) => {
                  const currentIndex = columns.findIndex((entry) => entry.id === item.status);
                  const previousStatus = currentIndex > 0 ? columns[currentIndex - 1].id : null;
                  const nextStatus = currentIndex < columns.length - 1 ? columns[currentIndex + 1].id : null;
                  const draft = drafts[item.id] ?? { note: "", next_follow_up_at: "" };

                  return (
                    <article 
                      key={item.id} 
                      className="rounded-[24px] bg-mist p-4 opacity-0 animate-slide-up hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 border border-transparent hover:border-teal/10"
                      style={{ animationDelay: `${index * 80}ms` }}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-ink leading-tight">{item.opportunity.title}</p>
                          <p className="mt-1 text-sm text-slate">{item.opportunity.organization}</p>
                        </div>
                        <span className="rounded-full bg-white px-3 py-1 text-[11px] font-medium uppercase tracking-[0.16em] text-teal">
                          {item.opportunity.type}
                        </span>
                      </div>

                      <p className="mt-3 text-[10px] uppercase tracking-[0.16em] text-slate font-medium">
                        {item.opportunity.domain} | {item.opportunity.mode} | deadline {formatDate(item.opportunity.deadline_at)}
                      </p>

                      <div className="mt-4 space-y-3">
                        <label className="grid gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-slate">
                          Notes
                          <textarea
                            value={draft.note}
                            onChange={(event) =>
                              setDrafts((current) => ({
                                ...current,
                                [item.id]: {
                                  ...current[item.id],
                                  note: event.target.value
                                }
                              }))
                            }
                            className="min-h-24 rounded-2xl border border-teal/10 bg-white px-3 py-2 text-sm text-ink outline-none transition-shadow focus:shadow-md"
                          />
                        </label>

                        <label className="grid gap-2 text-[10px] font-medium uppercase tracking-[0.16em] text-slate">
                          Follow-up
                          <input
                            type="date"
                            value={draft.next_follow_up_at}
                            onChange={(event) =>
                              setDrafts((current) => ({
                                ...current,
                                [item.id]: {
                                  ...current[item.id],
                                  next_follow_up_at: event.target.value
                                }
                              }))
                            }
                            className="rounded-2xl border border-teal/10 bg-white px-3 py-2 text-sm text-ink outline-none transition-shadow focus:shadow-md"
                          />
                        </label>
                      </div>

                      <div className="mt-4 flex flex-wrap gap-2">
                        {previousStatus ? (
                          <button
                            type="button"
                            disabled={isPending}
                            onClick={() => patchApplication(item.id, { status: previousStatus })}
                            className="rounded-full border border-teal/20 bg-white px-3 py-2 text-xs font-medium text-teal hover:bg-teal/5 transition-colors"
                          >
                            Move back
                          </button>
                        ) : null}
                        {nextStatus ? (
                          <button
                            type="button"
                            disabled={isPending}
                            onClick={() => patchApplication(item.id, { status: nextStatus })}
                            className="rounded-full bg-ink px-3 py-2 text-xs font-medium text-mist hover:scale-105 transition-transform"
                          >
                            Move forward
                          </button>
                        ) : null}
                        <button
                          type="button"
                          disabled={isPending}
                          onClick={() =>
                            patchApplication(item.id, {
                              note: draft.note,
                              next_follow_up_at: draft.next_follow_up_at ? `${draft.next_follow_up_at}T00:00:00.000Z` : null
                            })
                          }
                          className="rounded-full border border-ink/10 bg-white px-3 py-2 text-xs font-medium text-ink hover:bg-ink/5 transition-colors"
                        >
                          Save card
                        </button>
                      </div>

                      <div className="mt-3 flex flex-wrap gap-3 text-xs font-medium">
                        <Link href={`/opportunities/${item.opportunity.slug}`} className="text-teal hover:underline transition-colors">
                          Open detail
                        </Link>
                        <button
                          type="button"
                          disabled={isPending}
                          onClick={() => setItemToDelete(item.id)}
                          className="text-coral hover:text-red-600 transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    </article>
                  );
                })
              )}
            </div>
          </section>
        ))}
      </div>

      {message ? <p className="mt-4 rounded-2xl bg-mist px-4 py-3 text-sm text-slate animate-slide-up">{message}</p> : null}

      <ConfirmationModal
        isOpen={itemToDelete !== null}
        title="Remove Application"
        description="Are you sure you want to remove this application from your Kanban board?"
        confirmText="Yes, remove it"
        onConfirm={removeItem}
        onCancel={() => setItemToDelete(null)}
        isPending={isPending}
      />
    </div>
  );
}
