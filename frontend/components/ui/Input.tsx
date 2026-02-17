/**
 * Input Component
 * Text input with validation and error states
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, ...props }, ref) => (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-sm font-medium text-slate-700">{label}</label>}
      <input
        ref={ref}
        className={cn(
          'rounded-lg border border-slate-300 px-3 py-2.5 text-sm transition-colors',
          'bg-white placeholder-slate-400',
          'focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
          'hover:border-slate-400',
          error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  )
);
Input.displayName = 'Input';

export { Input };
