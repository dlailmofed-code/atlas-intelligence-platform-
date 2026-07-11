'use client';

import * as React from 'react';
import Link from 'next/link';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      {/* Left side - Branding */}
      <div className="hidden flex-1 flex-col justify-between bg-gradient-to-br from-primary to-primary/80 p-12 lg:flex">
        <div>
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20">
              <span className="text-xl font-bold text-white">A</span>
            </div>
            <span className="text-2xl font-bold text-white">ATLAS</span>
          </Link>
        </div>
        
        <div className="space-y-6">
          <h1 className="text-4xl font-bold leading-tight text-white">
            AI-Powered Business Intelligence Platform
          </h1>
          <p className="text-lg text-white/80">
            Transform global information streams into actionable business intelligence using multi-source data processing, causal reasoning, and explainable AI.
          </p>
          
          <div className="grid grid-cols-2 gap-6 pt-8">
            <div className="rounded-lg bg-white/10 p-4 backdrop-blur">
              <div className="text-3xl font-bold text-white">500+</div>
              <div className="text-sm text-white/70">Data Sources</div>
            </div>
            <div className="rounded-lg bg-white/10 p-4 backdrop-blur">
              <div className="text-3xl font-bold text-white">10K+</div>
              <div className="text-sm text-white/70">Opportunities Found</div>
            </div>
            <div className="rounded-lg bg-white/10 p-4 backdrop-blur">
              <div className="text-3xl font-bold text-white">95%</div>
              <div className="text-sm text-white/70">Accuracy Rate</div>
            </div>
            <div className="rounded-lg bg-white/10 p-4 backdrop-blur">
              <div className="text-3xl font-bold text-white">24/7</div>
              <div className="text-sm text-white/70">Real-time Monitoring</div>
            </div>
          </div>
        </div>
        
        <div className="text-sm text-white/60">
          © 2026 ATLAS Platform. All rights reserved.
        </div>
      </div>
      
      {/* Right side - Auth Form */}
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
