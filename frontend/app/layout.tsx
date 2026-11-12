import type { ReactNode } from "react";

export const metadata = {
  title: "Recipe Management",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
