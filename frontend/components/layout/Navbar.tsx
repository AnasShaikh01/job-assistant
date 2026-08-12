"use client";

import Link from "next/link";
import { SignInButton, SignUpButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

export default function Navbar() {
  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-6 h-20 flex items-center justify-between">
        
        {/* Logo area */}
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center transition-transform group-hover:scale-105 shadow-sm">
              <span className="text-white font-bold text-xl leading-none">P</span>
            </div>
            <span className="font-bold text-xl text-charcoal tracking-tight">PrimeVex</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-charcoal/70">
          <Link href="#problem" className="hover:text-primary transition-colors">The Problem</Link>
          <Link href="#workflow" className="hover:text-primary transition-colors">How it Works</Link>
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
        </nav>

        {/* Auth CTA */}
        <div className="flex items-center gap-4">
          <SignInButton mode="modal">
            <button className="text-sm font-medium text-charcoal/70 hover:text-primary transition-colors">
              Log in
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <Button className="bg-primary text-white hover:bg-primary/90 shadow-sm">
              Get Started
            </Button>
          </SignUpButton>
        </div>
      </div>
    </header>
  );
}