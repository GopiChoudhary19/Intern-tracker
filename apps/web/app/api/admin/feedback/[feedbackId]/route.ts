import { NextResponse } from "next/server";

import { updateAdminFeedbackStatus } from "../../../../../lib/admin";
import { isCurrentUserAdmin } from "../../../../../lib/admin-auth";

type RouteProps = {
  params: {
    feedbackId: string;
  };
};

const ALLOWED_STATUSES = ["new", "reviewing", "planned", "resolved"];

export async function PATCH(request: Request, { params }: RouteProps) {
  // The browser never has the admin token (it is a server secret), so the old header check rejected every
  // request from the admin page; authorise the signed-in admin instead.
  if (!(await isCurrentUserAdmin())) {
    return NextResponse.json({ detail: "Admin access required" }, { status: 403 });
  }
  try {
    const payload = await request.json();
    
    // Validate status enum
    if (!ALLOWED_STATUSES.includes(payload.status)) {
      return NextResponse.json(
        { detail: `Invalid status. Allowed values: ${ALLOWED_STATUSES.join(", ")}` },
        { status: 400 }
      );
    }
    
    const response = await updateAdminFeedbackStatus(params.feedbackId, payload.status);
    return NextResponse.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Feedback update failed";
    return NextResponse.json({ detail: message }, { status: 400 });
  }
}
