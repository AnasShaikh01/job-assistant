import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/landing/Hero";
import ProblemSection from "@/components/landing/ProblemSection";
import WorkflowSection from "@/components/landing/WorkflowSection";
import FeatureSection from "@/components/landing/FeatureSection";
import ProductPreview from "@/components/landing/ProductPreview";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/layout/Footer";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen selection:bg-accent selection:text-primary">
      <Navbar />
      
      <main className="flex-1 flex flex-col">
        <Hero />
        <ProblemSection />
        <WorkflowSection />
        <FeatureSection />
        <ProductPreview />
        <CTASection />
      </main>

      <Footer />
    </div>
  );
}