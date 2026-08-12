"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const pricingTiers = [
  {
    name: "Starter",
    description: "Perfect for casual job seekers updating their baseline resume.",
    price: "0",
    features: [
      "Upload and Parse 1 Base Resume",
      "Basic Candidate Knowledge Base",
      "3 Job Descriptions Matches per month",
      "Standard PDF Export",
    ],
    buttonText: "Start for Free",
    isPremium: false,
  },
  {
    name: "PrimeVex Pro",
    description: "The complete arsenal for active job hunters targeting top-tier tech roles.",
    price: "29",
    features: [
      "Unlimited Job Description Matches",
      "Dynamic ATS-Tailored Resume Generation",
      "AI Cover Letter & HR Email Engine",
      "AI Interview Simulator (Technical & Behavioral)",
      "Deep Company Intelligence Insights",
      "Advanced Skill Gap Analysis",
      "Visual Pipeline Tracker",
    ],
    buttonText: "Upgrade to Pro",
    isPremium: true,
  }
];

export default function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(true);

  return (
    <section id="pricing" className="py-24 md:py-32 bg-surface relative overflow-hidden">
      <div className="mx-auto max-w-7xl px-6 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge 
            variant="secondary" 
            className="mb-6 bg-accent/60 text-primary border border-primary/20 px-4 py-1.5 text-sm font-medium shadow-sm"
          >
            Simple Pricing
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-charcoal tracking-tight mb-6 leading-tight">
            Invest in your <br className="hidden md:block"/>
            career trajectory.
          </h2>
          <p className="text-lg text-charcoal/70 leading-relaxed mb-8">
            Start for free, upgrade when you are ready to automate your entire job hunt.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-3">
            <span className={`text-sm font-medium ${!isAnnual ? "text-charcoal" : "text-charcoal/50"}`}>Monthly</span>
            <button 
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isAnnual ? "translate-x-6" : "translate-x-1"}`} />
            </button>
            <span className={`text-sm font-medium ${isAnnual ? "text-charcoal" : "text-charcoal/50"}`}>
              Annually <span className="text-primary text-xs ml-1 bg-accent/60 px-2 py-0.5 rounded-full font-bold">Save 20%</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto items-center">
          
          {/* Starter Tier */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="bg-white border border-border rounded-[2rem] p-8 md:p-10 shadow-sm transition-transform duration-300 hover:-translate-y-1"
          >
            <h3 className="text-2xl font-bold text-charcoal mb-2">{pricingTiers[0].name}</h3>
            <p className="text-charcoal/70 text-sm mb-6 h-10">{pricingTiers[0].description}</p>
            <div className="mb-8">
              <span className="text-5xl font-bold text-charcoal">${pricingTiers[0].price}</span>
              <span className="text-charcoal/50 font-medium">/month</span>
            </div>
            <ul className="space-y-4 mb-8">
              {pricingTiers[0].features.map((feature, i) => (
                <li key={i} className="flex items-start gap-3 text-charcoal/80 text-sm">
                  <svg className="w-5 h-5 text-charcoal/30 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <Button variant="outline" className="w-full h-12 text-base border-border text-charcoal hover:bg-surface transition-colors">
              {pricingTiers[0].buttonText}
            </Button>
          </motion.div>

          {/* Premium Tier (On-brand Light Theme Highlight) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative bg-white rounded-[2rem] border-2 border-primary p-8 md:p-10 shadow-[0_12px_40px_-10px_rgba(16,185,129,0.2)] transition-transform duration-300 hover:-translate-y-1"
          >
            {/* Absolute badge */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest shadow-md z-20">
              Most Popular
            </div>

            <div className="relative z-10 h-full flex flex-col">
              <h3 className="text-2xl font-bold text-charcoal mb-2">{pricingTiers[1].name}</h3>
              <p className="text-charcoal/70 text-sm mb-6 h-10">{pricingTiers[1].description}</p>
              
              <div className="mb-8 flex items-baseline gap-1">
                <span className="text-5xl font-bold text-charcoal">
                  ${isAnnual ? Math.round(Number(pricingTiers[1].price) * 0.8) : pricingTiers[1].price}
                </span>
                <span className="text-charcoal/50 font-medium">/month</span>
              </div>
              
              <ul className="space-y-4 mb-8 flex-grow">
                {pricingTiers[1].features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-charcoal/80 text-sm font-medium">
                    <svg className="w-5 h-5 text-primary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              
              <Button className="w-full h-12 text-base bg-primary text-white hover:bg-primary/90 transition-all shadow-md hover:shadow-lg">
                {pricingTiers[1].buttonText}
              </Button>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}