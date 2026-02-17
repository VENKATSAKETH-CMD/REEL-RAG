/**
 * Auth Layout
 * Wrap auth pages without full layout
 */

import React from 'react';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
