import { Button } from "@/components/ui/button";
import { FlaskConical, RotateCcw } from "lucide-react";

type HeaderProps = {
    onReset: () => void;
};

export default function Header({ onReset }: HeaderProps) {
    return (
        <div className="flex flex-col gap-4 rounded-xl bg-background p-6 shadow-sm md:flex-row md:items-center md:justify-between">
            <div className="space-y-2">
                <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-primary/10 p-2">
                        <FlaskConical className="h-6 w-6 text-primary" />
                    </div>

                    <h1 className="text-3xl font-bold tracking-tight">
                        Job Assistant Test Lab
                    </h1>
                </div>
            </div>

            <Button
                variant="outline"
                className="gap-2"
                onClick={onReset}
            >
                <RotateCcw className="h-4 w-4" />
                Reset Session
            </Button>
        </div>
    );
}