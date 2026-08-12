"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, MotionValue } from "framer-motion";
import { Badge } from "@/components/ui/badge";

interface PipelineStep {
  id: number;
  title: string;
  description: string;
  icon: string;
  isLast?: boolean;
}

interface StackedCardProps {
  index: number;
  step: PipelineStep;
  progress: MotionValue<number>;
}

const pipelineSteps: PipelineStep[] = [
  {
    id: 1,
    title: "Candidate Engine",
    description: "Upload your resume once. We extract, clean, and map your history into a structured Candidate Knowledge Base (CKB). The static PDF is never used again.",
    icon: "1"
  },
  {
    id: 2,
    title: "Job Engine",
    description: "Paste a JD or URL. Our system extracts responsibilities and normalizes skills to build a precise Job Knowledge Base (JKB).",
    icon: "2"
  },
  {
    id: 3,
    title: "Matching Engine",
    description: "We pit your CKB against the JKB to reveal your exact Match Score, highlight missing skills, and identify the critical ATS keywords you need.",
    icon: "3"
  },
  {
    id: 4,
    title: "Dynamic Generation",
    description: "Our AI doesn't rewrite PDFs. It dynamically generates a perfectly tailored, ATS-compliant resume, cover letter, and HR email from the ground up.",
    icon: "4"
  },
  {
    id: 5,
    title: "Track & Prep",
    description: "Track your application from 'Saved' to 'Offer'. When the time comes, our engine generates technical and behavioral questions to prep you for the interview.",
    icon: "✨",
    isLast: true
  }
];

export default function WorkflowSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  return (
    <section ref={containerRef} id="workflow" className="relative bg-background pt-32 pb-32">
      {/* Subtle Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-accent/30 blur-[120px] rounded-full pointer-events-none" />

      <div className="mx-auto max-w-7xl px-6 flex flex-col lg:flex-row gap-12 lg:gap-20 relative z-10">
        
        {/* Left Column: Sticky Context */}
        <div className="w-full lg:w-5/12 lg:sticky lg:top-40 h-fit mb-12 lg:mb-0 space-y-6">
          <Badge 
            variant="secondary" 
            className="bg-surface text-primary border border-border px-4 py-1.5 text-sm font-medium shadow-sm"
          >
            The Architecture
          </Badge>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-charcoal tracking-tight leading-[1.1]">
            Engineered for <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-hover">precision.</span>
          </h2>
          <p className="text-lg text-charcoal/70 leading-relaxed max-w-md">
            We never prompt AI with raw text. PrimeVex uses a deterministic pipeline to parse your data once, structured perfectly for our specialized matching engines.
          </p>
        </div>

        {/* Right Column: Native Sticky Stack */}
        <div className="w-full lg:w-7/12 relative">
          {pipelineSteps.map((step, index) => (
            <StackedCard
              key={step.id}
              index={index}
              step={step}
              progress={scrollYProgress}
            />
          ))}
          {/* Spacer to allow the final card to fully pin and settle before unmounting the section */}
          <div className="h-[70vh]" />
        </div>
      </div>
    </section>
  );
}

function StackedCard({ index, step, progress }: StackedCardProps) {
  // Increased spacing for a cleaner stack
  const CARD_OFFSET = 40; 
  // Reduced top sticky point so it sits closer to the center of the viewport
  const topPosition = 100 + index * CARD_OFFSET;

  // Overlapping animation triggers for buttery smooth sequence
  const start = index * 0.14;
  const end = start + 0.32;

  // As per your recommendation: No scaling, no dimming. 
  // Just a premium -25px upward shift as the next card slides over it.
  const y = useTransform(
    progress,
    [start, end],
    [0, -25]
  );

  const borderClass = step.isLast ? "border-2 border-primary" : "border border-border/80";

  return (
    <div
      className="sticky flex flex-col justify-start"
      style={{
        top: `${topPosition}px`,
        // Uniform height for all cards creates a reliable scroll track
        height: "60vh",
      }}
    >
      <motion.div
        style={{
          y: step.isLast ? 0 : y, // The last card doesn't need to be pushed up
          transformOrigin: "top center",
        }}
        className={`w-full bg-surface shadow-soft rounded-[2rem] p-8 md:p-12 ${borderClass} relative`}
      >
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold mb-6 ${step.isLast ? 'bg-primary text-white shadow-md' : 'bg-accent/40 text-primary border border-accent/80'}`}>
          {step.icon}
        </div>
        <h3 className="text-2xl md:text-3xl font-bold text-charcoal mb-4 tracking-tight">
          {step.title}
        </h3>
        <p className="text-charcoal/70 text-base md:text-lg leading-relaxed">
          {step.description}
        </p>
      </motion.div>
    </div>
  );
}