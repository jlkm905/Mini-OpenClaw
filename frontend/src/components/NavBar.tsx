'use client';

import { Cpu } from 'lucide-react';

export default function NavBar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 glass-nav flex items-center px-5">
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center">
          <Cpu className="w-4 h-4 text-white" />
        </div>
        <span className="text-sm font-semibold text-gray-900 tracking-tight">
          mini <span className="text-accent">OpenClaw</span>
        </span>
      </div>
    </header>
  );
}
