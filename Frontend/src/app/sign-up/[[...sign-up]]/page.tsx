import { SignUp } from "@clerk/nextjs";
import { Sparkles } from "lucide-react";
import Link from "next/link";

export default function SignUpPage() {
  return (
    <div className="min-h-screen w-full bg-[#09090b] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Brand Header */}
      <div className="flex flex-col items-center space-y-2 mb-8 relative z-10 text-center">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 text-white">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">
            StudyPack<span className="text-indigo-400">AI</span>
          </span>
        </Link>
        <p className="text-xs text-neutral-400">
          Create your account to start generating intelligent study packs
        </p>
      </div>

      {/* Clerk SignUp Component */}
      <div className="relative z-10">
        <SignUp
          appearance={{
            elements: {
              card: "bg-neutral-900/90 border border-neutral-800 shadow-2xl backdrop-blur-xl rounded-2xl",
              headerTitle: "text-white font-bold",
              headerSubtitle: "text-neutral-400",
              socialButtonsBlockButton:
                "bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700",
              formButtonPrimary:
                "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30",
              formFieldInput:
                "bg-neutral-950 border-neutral-800 text-white placeholder:text-neutral-600 focus:border-indigo-500",
              footerActionLink: "text-indigo-400 hover:text-indigo-300",
              dividerLine: "bg-neutral-800",
              dividerText: "text-neutral-500",
            },
          }}
        />
      </div>
    </div>
  );
}
