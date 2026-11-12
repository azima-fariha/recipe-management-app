import { InspirationForm } from "@/components/InspirationForm";

// Route protection is enforced by middleware.ts (every path but /login and
// /signup requires a valid session cookie), so this page can render the
// client-side form directly.
export default function InspirationPage() {
  return <InspirationForm />;
}
