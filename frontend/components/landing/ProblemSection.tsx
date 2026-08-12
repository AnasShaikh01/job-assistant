import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ProblemSection() {
  const problems = [
    {
      title: "Static Resumes",
      description: "You are applying to dynamic jobs with a static PDF. Tweaking it manually for every application takes hours and leads to version control chaos.",
      icon: "📄",
    },
    {
      title: "Disconnected Jobs",
      description: "Job descriptions are dense blocks of text. Without structured analysis, you miss critical keywords that ATS scanners are looking for.",
      icon: "🎯",
    },
    {
      title: "Lost Applications",
      description: "Scattered spreadsheets and endless browser tabs. Keeping track of what you submitted, when, and to whom becomes a full-time job itself.",
      icon: "📉",
    },
  ];

  return (
    <section id="problem" className="py-24 bg-surface">
      <div className="mx-auto max-w-7xl px-6">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge 
            variant="secondary" 
            className="mb-6 bg-accent/60 text-primary border border-primary/10 px-4 py-1.5 text-sm font-medium shadow-sm"
          >
            The Reality
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold text-charcoal tracking-tight mb-6">
            The job hunt is broken.
          </h2>
          <p className="text-lg text-charcoal/70 leading-relaxed">
            Managing multiple resume versions, decoding vague job descriptions, and tracking applications across platforms is exhausting.
          </p>
        </div>

        {/* 3-Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {problems.map((problem, index) => (
            <Card 
              key={index} 
              className="group flex flex-col h-full bg-background border-border hover:border-primary/30 transition-all duration-300 hover:shadow-lift hover:-translate-y-1"
            >
              <CardHeader>
                <div className="w-14 h-14 rounded-xl bg-accent/40 border border-accent/60 flex items-center justify-center text-2xl mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:bg-accent/70">
                  {problem.icon}
                </div>
                <CardTitle className="text-xl font-bold text-charcoal">
                  {problem.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-charcoal/70 leading-relaxed text-sm">
                  {problem.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
        
      </div>
    </section>
  );
}