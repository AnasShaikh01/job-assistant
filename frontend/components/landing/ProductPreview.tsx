"use client";

import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";

export default function ProductPreview() {
  const previews = [
    {
      title: "Command Central for your Career",
      badge: "Dashboard",
      description: "Get a bird's-eye view of your active applications, recent matches, and upcoming interviews. Everything is interconnected and updates in real-time.",
      reversed: false,
    },
    {
      title: "Your Career, Structured",
      badge: "Candidate Profile",
      description: "Move away from messy Word docs. Manage your entire work history, skills, and projects in a structured knowledge base that powers our AI engine.",
      reversed: true,
    },
    {
      title: "Decode Job Descriptions",
      badge: "Job Analysis",
      description: "Stop guessing what recruiters want. Upload a job posting and instantly see the exact skills, responsibilities, and keywords you need to highlight.",
      reversed: false,
    },
  ];

  return (
    <section id="preview" className="py-24 md:py-32 bg-background overflow-hidden relative">
      <div className="mx-auto max-w-7xl px-6 space-y-32 relative z-10">
        
        {previews.map((item, index) => (
          <div 
            key={index} 
            className={`flex flex-col gap-12 lg:gap-20 items-center ${
              item.reversed ? "lg:flex-row-reverse" : "lg:flex-row"
            }`}
          >
            {/* Text Content */}
            <motion.div 
              initial={{ opacity: 0, x: item.reversed ? 30 : -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="w-full lg:w-5/12 space-y-6"
            >
              <Badge variant="secondary" className="bg-accent/60 text-primary border border-primary/10 px-4 py-1.5 text-sm font-medium shadow-sm">
                {item.badge}
              </Badge>
              <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-charcoal leading-tight tracking-tight">
                {item.title}
              </h3>
              <p className="text-lg text-charcoal/70 leading-relaxed">
                {item.description}
              </p>
            </motion.div>

            {/* Image/Mockup Showcase */}
            <motion.div 
              initial={{ opacity: 0, x: item.reversed ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
              className="w-full lg:w-7/12 relative group perspective-1000"
            >
              {/* Soft ambient background glow */}
              <div className="absolute -inset-4 bg-gradient-to-tr from-accent to-surface blur-2xl opacity-40 rounded-3xl -z-10 group-hover:opacity-80 transition-opacity duration-700" />
              
              {/* Browser Window Container */}
              <div className="relative rounded-2xl border border-border bg-surface p-2 shadow-sm transition-all duration-700 hover:-translate-y-2 hover:shadow-xl">
                <div className="rounded-xl overflow-hidden bg-background border border-border/60 aspect-[4/3] md:aspect-[16/9] flex flex-col relative">
                  
                  {/* Mock Browser/App Header */}
                  <div className="h-10 border-b border-border/60 bg-surface flex items-center px-4 gap-2 shrink-0">
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-charcoal/20" />
                      <div className="w-2.5 h-2.5 rounded-full bg-charcoal/20" />
                      <div className="w-2.5 h-2.5 rounded-full bg-charcoal/20" />
                    </div>
                  </div>
                  
                  {/* Your Original Elegant Placeholder */}
                  <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-8 text-center bg-gradient-to-br from-background to-surface">
                     <div className="border-2 border-dashed border-primary/20 bg-primary/5 rounded-xl w-full h-full flex flex-col items-center justify-center transition-colors duration-500 group-hover:border-primary/40 group-hover:bg-primary/10">
                       <span className="text-primary/60 font-semibold text-lg md:text-xl tracking-wide">
                         [ {item.badge} UI Screenshot ]
                       </span>
                     </div>
                  </div>

                </div>
              </div>
            </motion.div>
          </div>
        ))}

      </div>
    </section>
  );
}