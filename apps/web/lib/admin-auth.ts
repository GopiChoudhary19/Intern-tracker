import { getProfile } from "./api";
import { getServerAuthToken } from "./session";

// The admin token lives only on the server, so every admin page and admin API route must first prove that the
// signed-in user is an administrator. Admins are listed by email in INTERN_TRACKER_ADMIN_EMAILS (comma separated).
export function getAdminEmails(): string[] {
  return (process.env.INTERN_TRACKER_ADMIN_EMAILS ?? "")
    .split(",")
    .map((email) => email.trim().toLowerCase())
    .filter(Boolean);
}

export async function isCurrentUserAdmin(): Promise<boolean> {
  const allowed = getAdminEmails();
  const token = await getServerAuthToken();
  if (!token || allowed.length === 0) {
    return false;
  }
  try {
    const profile = await getProfile(token);
    return Boolean(profile.email) && allowed.includes(profile.email!.toLowerCase());
  } catch {
    // an expired or revoked session is simply not an admin
    return false;
  }
}
