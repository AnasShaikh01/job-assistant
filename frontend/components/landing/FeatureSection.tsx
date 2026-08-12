"use client";

import { Badge } from "@/components/ui/badge";
import MagicBento from "@/components/ui/magic-bento";

export default function FeatureSection() {
  return (
    <section id="features" className="py-24 md:py-32 bg-surface relative overflow-hidden">
      <div className="mx-auto max-w-7xl px-6 relative z-10 flex flex-col items-center">
        
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge 
            variant="secondary" 
            className="mb-6 bg-accent/60 text-primary border border-primary/10 px-4 py-1.5 text-sm font-medium shadow-sm"
          >
            The Ecosystem
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-charcoal tracking-tight mb-6 leading-tight">
            Everything you need. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-hover">Built into one platform.</span>
          </h2>
          <p className="text-lg text-charcoal/70 leading-relaxed">
            PrimeVex doesnt just format documents. It provides end-to-end career intelligence to give you an unfair advantage.
          </p>
        </div>

        <div className="w-full">
          <MagicBento />
        </div>

      </div>
    </section>
  );
}