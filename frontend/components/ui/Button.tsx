/**
 * Button Component
 * Primary CTA with variants and loading state
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200 focus-ring disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-cyan-500 text-white hover:bg-cyan-600 active:scale-95',
        secondary: 'bg-slate-200 text-slate-900 hover:bg-slate-300 active:scale-95',
        outline: 'border border-slate-300 text-slate-900 hover:bg-slate-50 active:scale-95',
        ghost: 'text-slate-700 hover:bg-slate-100 active:scale-95',
        danger: 'bg-red-500 text-white hover:bg-red-600 active:scale-95',
      },
      size: {
        sm: 'px-3 py-2 text-sm',
        md: 'px-4 py-2.5 text-base',
        lg: 'px-6 py-3 text-lg',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, fullWidth, isLoading, disabled, children, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, fullWidth }), className)}
      disabled={disabled || isLoading}
      ref={ref}
      {...props}
    >
      {isLoading && <Spinner size="sm" />}
      {children}
    </button>
  )
);
Button.displayName = 'Button';

function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }[size];

  return (
    <div className={cn('animate-spin rounded-full border-2 border-current border-t-transparent', sizeClass)} />
  );
}

export { Button, Spinner };
