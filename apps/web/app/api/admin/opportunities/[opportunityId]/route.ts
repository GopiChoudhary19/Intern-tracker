import { NextResponse } from "next/server";

import { deleteAdminOpportunity, updateAdminOpportunity } from "../../../../../lib/admin";
import { isCurrentUserAdmin } from "../../../../../lib/admin-auth";

type RouteProps = {
  params: {
    opportunityId: string;
  };
};

const FORBIDDEN = { detail: "Admin access required" };

export async function PATCH(request: Request, { params }: RouteProps) {
  if (!(await isCurrentUserAdmin())) {
    return NextResponse.json(FORBIDDEN, { status: 403 });
  }
  try {
    const payload = await request.json();
    const response = await updateAdminOpportunity(params.opportunityId, payload);
    return NextResponse.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Opportunity update failed";
    return NextResponse.json({ detail: message }, { status: 400 });
  }
}

export async function DELETE(_: Request, { params }: RouteProps) {
  if (!(await isCurrentUserAdmin())) {
    return NextResponse.json(FORBIDDEN, { status: 403 });
  }
  try {
    const response = await deleteAdminOpportunity(params.opportunityId);
    return NextResponse.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Opportunity delete failed";
    return NextResponse.json({ detail: message }, { status: 400 });
  }
}
