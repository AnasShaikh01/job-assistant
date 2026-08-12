"use client";

import { motion } from "framer-motion";
import { SignUpButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden bg-background">
      
      {/* Subtle Sage Glow to break the flat white, avoiding the solid green wall */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[600px] bg-[radial-gradient(ellipse_at_top,_var(--color-accent),_transparent_70%)] opacity-50 pointer-events-none" />

      <div className="mx-auto max-w-7xl px-6 relative z-10">
        
        {/* Content with Fade Up Animation */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col items-center text-center max-w-4xl mx-auto mb-20 space-y-8"
        >
          <div className="inline-flex items-center rounded-full bg-surface border border-border px-4 py-1.5 text-sm font-medium text-charcoal/80 shadow-sm">
            ✨ Introducing the next generation of career tools
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-charcoal leading-[1.1]">
            Build your <span className="text-primary">AI Career</span> Workspace
          </h1>
          
          <p className="text-lg md:text-xl text-charcoal/70 max-w-2xl leading-relaxed">
            One premium platform to analyze job descriptions, optimize your knowledge base, generate tailored documents, and track every application.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4 w-full">
            <SignUpButton mode="modal">
              <Button size="lg" className="w-full sm:w-auto bg-primary text-white hover:bg-primary/90 shadow-soft transition-all hover:shadow-lift h-14 px-8 text-base">
                Get Started for Free
              </Button>
            </SignUpButton>
            <Button variant="outline" size="lg" className="w-full sm:w-auto border-border bg-surface text-charcoal hover:bg-accent/50 h-14 px-8 text-base shadow-sm">
              Watch Demo
            </Button>
          </div>
        </motion.div>

        {/* Dashboard Mockup with 3D Tilt Entrance */}
        <motion.div 
          initial={{ opacity: 0, y: 80, rotateX: 15 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 1.2, delay: 0.2, ease: "easeOut" }}
          style={{ perspective: 1200 }}
          className="relative mx-auto max-w-5xl"
        >
          <div className="relative rounded-2xl border border-border bg-surface/50 p-2 shadow-lift backdrop-blur-xl">
            <div className="rounded-xl overflow-hidden border border-border bg-background aspect-[4/3] md:aspect-[16/9] flex flex-col relative">
              
              {/* Mock Browser/App Header */}
              <div className="h-12 border-b border-border bg-surface flex items-center px-4 gap-2 w-full">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-border" />
                  <div className="w-3 h-3 rounded-full bg-border" />
                  <div className="w-3 h-3 rounded-full bg-border" />
                </div>
              </div>

              {/* Internal Mockup Area */}
              <div className="flex-1 flex items-center justify-center bg-[radial-gradient(ellipse_at_center,_var(--color-accent)_0%,_transparent_60%)] opacity-30">
                <p className="text-primary font-bold text-xl tracking-widest uppercase">
                  [ Dashboard Interface ]
                </p>
              </div>
              
            </div>
          </div>
        </motion.div>
        
      </div>
    </section>
  );
}