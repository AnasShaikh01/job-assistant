"use client";

import { SignIn } from "@clerk/nextjs";
import Link from "next/link";
import { motion } from "framer-motion";

export default function SignInPage() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center bg-[#050505] overflow-hidden selection:bg-primary/30 selection:text-white">
      
      {/* Abstract Background Effects */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Floating Logo */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-20 mb-8"
      >
        <Link href="/" className="flex items-center gap-3 group">
          <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center transition-transform duration-500 group-hover:scale-105 group-hover:shadow-[0_0_30px_rgba(16,185,129,0.4)]">
            <span className="text-white font-bold text-lg leading-none tracking-tighter">P</span>
          </div>
          <span className="font-bold text-3xl text-white tracking-tight">PrimeVex</span>
        </Link>
      </motion.div>

      {/* Glassmorphic Modal Wrapper */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
        className="relative z-20 w-full max-w-md px-6"
      >
        {/* Subtle glowing border mask behind the card */}
        <div className="absolute inset-0 px-6 blur-md bg-gradient-to-b from-primary/20 to-transparent opacity-50 pointer-events-none rounded-[2rem]" />

        <SignIn 
          path="/sign-in" 
          routing="path" 
          signUpUrl="/sign-up" 
          appearance={{
            variables: {
              colorPrimary: "#10b981", // Emerald
              colorBackground: "transparent",
              colorDanger: "#ef4444",
            },
            elements: {
              card: "bg-black/40 backdrop-blur-2xl border border-white/10 shadow-[0_8px_40px_-12px_rgba(16,185,129,0.15)] rounded-3xl w-full",
              headerTitle: "text-white font-bold text-2xl tracking-tight",
              headerSubtitle: "text-zinc-400 text-sm",
              socialButtonsBlockButton: "bg-white/5 border border-white/10 text-white hover:bg-white/10 hover:border-white/20 transition-all",
              socialButtonsBlockButtonText: "font-semibold",
              dividerLine: "bg-white/10",
              dividerText: "text-zinc-500",
              formFieldLabel: "text-zinc-300 font-medium",
              formFieldInput: "bg-white/5 border border-white/10 focus:border-primary focus:ring-1 focus:ring-primary text-white placeholder:text-zinc-600 transition-all h-11",
              formButtonPrimary: "bg-primary text-white font-bold hover:bg-primary/90 transition-all h-11 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] hover:-translate-y-0.5",
              footerActionLink: "text-primary hover:text-emerald-400 font-semibold transition-colors",
              identityPreviewText: "text-zinc-300",
              identityPreviewEditButton: "text-primary hover:text-emerald-400",
              footerActionText: "text-zinc-400",
            }
          }}
        />
      </motion.div>
      
    </main>
  );
}