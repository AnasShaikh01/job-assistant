"use client";

import React, { useRef, useEffect, useState } from 'react';
import { gsap } from 'gsap';

export interface BentoCardProps {
  title: string;
  description: string;
  label: string;
  icon: React.ReactNode;
  className: string;
}

// PrimeVex Emerald Green for the mouse-tracking border glow
const GLOW_COLOR = '16, 185, 129'; 
const MOBILE_BREAKPOINT = 768;

const cardData: BentoCardProps[] = [
  {
    title: 'Candidate Knowledge Base',
    description: 'Upload your resume once. We parse it into a deterministic, queryable knowledge base.',
    label: 'Foundation',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
      </svg>
    ),
    className: 'md:col-span-4 md:row-span-1', 
  },
  {
    title: 'Job Engine',
    description: 'Extracts deep ATS requirements from any URL.',
    label: 'Analysis',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
      </svg>
    ),
    className: 'md:col-span-2 md:row-span-1', 
  },
  {
    title: 'Matching Engine',
    description: 'Calculates precision scores and identifies critical skill gaps instantly.',
    label: 'Algorithm',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <circle cx="12" cy="12" r="6"></circle>
        <circle cx="12" cy="12" r="2"></circle>
      </svg>
    ),
    className: 'md:col-span-2 md:row-span-1',
  },
  {
    title: 'AI Document Generation',
    description: 'Builds tailored, ATS-compliant documents from the ground up without hallucinating your experience.',
    label: 'Output',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"></path>
      </svg>
    ),
    className: 'md:col-span-4 md:row-span-1',
  },
  {
    title: 'Interview Simulator',
    description: 'Role-specific technical & behavioral prep.',
    label: 'Practice',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
        <line x1="8" y1="23" x2="16" y2="23"></line>
      </svg>
    ),
    className: 'md:col-span-3 md:row-span-1',
  },
  {
    title: 'Pipeline Tracker',
    description: 'Manage your entire journey from "Saved" to "Offer".',
    label: 'Management',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="9" y1="3" x2="9" y2="21"></line>
        <line x1="15" y1="3" x2="15" y2="21"></line>
      </svg>
    ),
    className: 'md:col-span-3 md:row-span-1',
  }
];

export default function MagicBento() {
  const [isMobile, setIsMobile] = useState(false);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= MOBILE_BREAKPOINT);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="w-full relative select-none" ref={gridRef}>
      <style>
        {`
          .card--border-glow::after {
            content: '';
            position: absolute;
            inset: 0;
            padding: 1.5px;
            background: radial-gradient(var(--glow-radius) circle at var(--glow-x) var(--glow-y),
                rgba(${GLOW_COLOR}, calc(var(--glow-intensity) * 0.8)) 0%,
                transparent 60%);
            border-radius: inherit;
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
          }
          
          .card--border-glow:hover::after {
            opacity: 1;
          }
          
          .card--border-glow:hover {
            box-shadow: 0 10px 40px -10px rgba(${GLOW_COLOR}, 0.15);
          }
        `}
      </style>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-6 auto-rows-[260px]">
        {cardData.map((card, index) => {
          const baseClassName = `card card--border-glow flex flex-col justify-between relative p-8 md:p-10 rounded-[24px] overflow-hidden bg-white border border-border shadow-sm cursor-default ${card.className}`;

          return (
            <div 
              key={index} 
              className={baseClassName}
              style={{
                '--glow-x': '50%',
                '--glow-y': '50%',
                '--glow-intensity': '0',
                '--glow-radius': '250px'
              } as React.CSSProperties}
              ref={el => {
                if (!el || isMobile) return;

                const handleMouseMove = (e: MouseEvent) => {
                  const rect = el.getBoundingClientRect();
                  const x = e.clientX - rect.left;
                  const y = e.clientY - rect.top;
                  
                  // Update CSS variables for the border glow mask
                  const relativeX = (x / rect.width) * 100;
                  const relativeY = (y / rect.height) * 100;
                  el.style.setProperty('--glow-x', `${relativeX}%`);
                  el.style.setProperty('--glow-y', `${relativeY}%`);
                  el.style.setProperty('--glow-intensity', '1');

                  // GSAP soft tilt and magnetism
                  const centerX = rect.width / 2;
                  const centerY = rect.height / 2;
                  const rotateX = ((y - centerY) / centerY) * -4; // Subtly tuned for professional look
                  const rotateY = ((x - centerX) / centerX) * 4;

                  gsap.to(el, {
                    rotateX,
                    rotateY,
                    x: (x - centerX) * 0.02,
                    y: (y - centerY) * 0.02,
                    duration: 0.3,
                    ease: 'power2.out',
                    transformPerspective: 1000
                  });
                };

                const handleMouseLeave = () => {
                  el.style.setProperty('--glow-intensity', '0');
                  gsap.to(el, {
                    rotateX: 0,
                    rotateY: 0,
                    x: 0,
                    y: 0,
                    duration: 0.5,
                    ease: 'power2.out'
                  });
                };

                el.addEventListener('mousemove', handleMouseMove);
                el.addEventListener('mouseleave', handleMouseLeave);
              }}
            >
              
              {/* Exact Original Header Structure (styled for light theme) */}
              <div className="card__header flex justify-between gap-3 relative text-charcoal z-10">
                <span className="card__label font-semibold text-sm tracking-widest uppercase text-primary">
                  {card.label}
                </span>
                <div className="text-primary/70">
                  {card.icon}
                </div>
              </div>

              {/* Exact Original Content Structure */}
              <div className="card__content flex flex-col relative text-charcoal mt-auto z-10">
                <h3 className="card__title font-bold text-xl md:text-2xl m-0 mb-2 tracking-tight">
                  {card.title}
                </h3>
                <p className="card__description text-sm md:text-base leading-relaxed opacity-80 line-clamp-2">
                  {card.description}
                </p>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}