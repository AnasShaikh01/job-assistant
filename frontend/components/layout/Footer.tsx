import Link from "next/link";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-surface border-t border-border py-12 md:py-16">
      <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row justify-between items-center gap-8 md:gap-6">
        
        {/* Brand */}
        <div className="flex flex-col items-center md:items-start">
          <Link href="/" className="flex items-center gap-2 mb-2 group">
            <div className="h-7 w-7 rounded-lg bg-primary flex items-center justify-center transition-transform duration-300 group-hover:scale-105 shadow-sm">
              <span className="text-white font-bold text-sm leading-none">P</span>
            </div>
            <span className="font-bold text-xl text-charcoal tracking-tight">PrimeVex</span>
          </Link>
          <p className="text-sm text-charcoal/60 font-medium">
            The Deterministic Career Engine.
          </p>
        </div>

        {/* Simple Links */}
        <div className="flex flex-wrap justify-center md:justify-end gap-6 md:gap-8 text-sm font-medium text-charcoal/70">
          <Link href="#preview" className="hover:text-primary transition-colors">Ecosystem</Link>
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
          <Link href="#" className="hover:text-primary transition-colors">Privacy</Link>
          <Link href="#" className="hover:text-primary transition-colors">Terms</Link>
        </div>
      </div>
      
      {/* Bottom Bar */}
      <div className="mx-auto max-w-7xl px-6 mt-12 pt-8 border-t border-border/50 flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-sm text-charcoal/50 font-medium">
          © {currentYear} PrimeVex Technologies. All rights reserved.
        </p>
        
        {/* Premium SaaS Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/30 border border-accent/50 cursor-default hover:bg-accent/50 transition-colors">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          <span className="text-xs text-charcoal/70 font-semibold tracking-wide">All systems operational</span>
        </div>
      </div>
    </footer>
  );
}