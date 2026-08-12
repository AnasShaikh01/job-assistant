export function OnboardingFAQ() {
    const faqs = [
        {
            q: "What file formats do you support?",
            a: "We currently support .PDF, .DOC, and .DOCX files up to 5MB in size. We highly recommend PDF for the most accurate layout parsing."
        },
        {
            q: "Is my data secure?",
            a: "Yes. Your resume is parsed in memory and the original file is immediately purged. We do not use your personal information to train public AI models."
        },
        {
            q: "What happens if the AI makes a mistake?",
            a: "The extraction is just the first step. Immediately after uploading, you'll be taken to an interactive dashboard where you can review, edit, and add to your extracted profile."
        },
        {
            q: "Do I have to do this every time?",
            a: "No! That's the beauty of PrimeVex. You upload your resume once to build your Knowledge Base. From then on, you generate targeted resumes directly from your saved profile."
        }
    ];

    return (
        <section className="py-24 bg-surface border-t border-border">
            <div className="max-w-4xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-charcoal mb-4">Frequently Asked Questions</h2>
                    <p className="text-charcoal/70">Everything you need to know about our extraction engine.</p>
                </div>
                
                <div className="space-y-6">
                    {faqs.map((faq, index) => (
                        <div key={index} className="bg-background border border-border rounded-2xl p-6 md:p-8 shadow-sm">
                            <h3 className="text-lg font-bold text-charcoal mb-3">{faq.q}</h3>
                            <p className="text-charcoal/70 leading-relaxed">{faq.a}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}