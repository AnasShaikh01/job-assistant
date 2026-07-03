import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { SignInButton, SignUpButton } from "@clerk/nextjs";

export default async function Home() {
  const { userId } = await auth();

  if (userId) {
    redirect("/dashboard");
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="max-w-2xl text-center space-y-8">
        <div className="space-y-4">

          <p className="text-lg text-gray-500">
            AI-powered Resume & Job Application Copilot
          </p>
        </div>

        <div className="flex justify-center gap-4">
          <SignUpButton mode="modal">
            <button className="rounded-lg bg-black px-6 py-3 text-white transition hover:bg-neutral-800">
              Get Started
            </button>
          </SignUpButton>

          <SignInButton mode="modal">
            <button className="rounded-lg border px-6 py-3 transition hover:bg-neutral-100">
              Sign In
            </button>
          </SignInButton>
        </div>
      </div>
    </main>
  );
}