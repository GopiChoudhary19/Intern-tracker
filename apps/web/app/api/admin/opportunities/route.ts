import { NextResponse } from "next/server";

import { createAdminOpportunity } from "../../../../lib/admin";
import { isCurrentUserAdmin } from "../../../../lib/admin-auth";

export async function POST(request: Request) {
  // this route forwards with the server-side admin token, so it must not be callable by anyone else
  if (!(await isCurrentUserAdmin())) {
    return NextResponse.json({ detail: "Admin access required" }, { status: 403 });
  }
  try {
    const payload = await request.json();
    const response = await createAdminOpportunity(payload);
    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Opportunity creation failed";
    return NextResponse.json({ detail: message }, { status: 400 });
  }
}
