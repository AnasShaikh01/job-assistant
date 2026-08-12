"use client";

import { motion } from "framer-motion";
import { SignUpButton } from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

export default function CTASection() {
  return (
    <section className="relative py-24 md:py-32 bg-primary overflow-hidden">
      
      {/* Subtle ambient glow for depth - avoiding custom CSS variables to prevent build errors */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-3xl h-[500px] bg-[radial-gradient(ellipse_at_center,_rgba(255,255,255,0.12)_0%,_transparent_70%)] pointer-events-none" />

      {/* Abstract geometric shapes for a premium SaaS feel */}
      <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-white opacity-[0.03] rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-80 h-80 bg-white opacity-[0.03] rounded-full blur-3xl pointer-events-none" />

      <div className="mx-auto max-w-5xl px-6 relative z-10 text-center">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="flex flex-col items-center"
        >
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-white mb-6 leading-tight">
            Stop applying in the dark. <br />
            <span className="text-white/80">Take control of your career.</span>
          </h2>
          
          <p className="text-lg md:text-xl text-white/70 max-w-2xl leading-relaxed mb-10">
            Join the next generation of professionals using PrimeVex to automate their job hunt, bypass the ATS, and land top-tier roles.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full">
            <SignUpButton mode="modal">
              <Button size="lg" className="w-full sm:w-auto bg-white text-primary hover:bg-surface shadow-[0_4px_14px_rgba(0,0,0,0.1)] transition-all hover:shadow-[0_6px_20px_rgba(0,0,0,0.15)] hover:-translate-y-0.5 h-14 px-10 text-base font-bold">
                Get Started for Free
              </Button>
            </SignUpButton>
            <Button variant="outline" size="lg" className="w-full sm:w-auto border-white/20 bg-white/5 text-white hover:bg-white/10 backdrop-blur-md h-14 px-10 text-base transition-colors">
              Talk to Sales
            </Button>
          </div>

          <p className="mt-8 text-sm text-white/50 font-medium">
            No credit card required. Free tier available forever.
          </p>
        </motion.div>
      </div>
    </section>
  );
}