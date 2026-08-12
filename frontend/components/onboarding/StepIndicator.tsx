export function StepIndicator({ currentStep }: { currentStep: number }) {
    return (
        <div className="flex items-center gap-2 mb-8">
            <div className={`h-1 w-12 rounded-full ${currentStep >= 1 ? 'bg-emerald-500' : 'bg-gray-800'}`} />
            <div className={`h-1 w-12 rounded-full ${currentStep >= 2 ? 'bg-emerald-500' : 'bg-gray-800'}`} />
            <span className="text-xs font-medium text-gray-500 ml-2 uppercase tracking-widest">
                Step {currentStep} of 2
            </span>
        </div>
    );
}