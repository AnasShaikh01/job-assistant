import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PrimeVex | The Career Command Center",
  description: "Automate your job hunt, bypass the ATS, and land top-tier roles.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
<<<<<<< HEAD
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col selection:bg-accent selection:text-primary">
        <ClerkProvider
          appearance={{
            variables: {
              colorPrimary: "#10b981", // Deep Emerald
              colorBackground: "#ffffff",
              colorDanger: "#ef4444",
            },
            elements: {
              card: "shadow-xl border border-border/50 rounded-2xl",
              headerTitle: "text-2xl font-bold tracking-tight text-charcoal",
              headerSubtitle: "text-charcoal/60",
              socialButtonsBlockButton: "border border-border bg-white hover:bg-surface text-charcoal transition-colors",
              formButtonPrimary: "bg-primary hover:bg-primary/90 text-white font-bold shadow-sm transition-all hover:-translate-y-0.5",
              formFieldInput: "bg-surface border-border focus:border-primary focus:ring-primary/20 transition-colors",
              footerActionLink: "text-primary font-semibold hover:text-primary/80",
            },
          }}
        >
          {children}
        </ClerkProvider>
      </body>
    </html>
=======
    <ClerkProvider>
      <html
        lang="en"
        className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      >
        <body>{children}</body>
      </html>
    </ClerkProvider>
>>>>>>> main
  );
}