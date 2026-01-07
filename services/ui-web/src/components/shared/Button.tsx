// src/components/shared/Button.tsx
import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
}

// Petit helper pour concaténer les classes sans dépendance externe
function cn(...parts: Array<string | undefined | null | false>): string {
  return parts.filter(Boolean).join(" ");
}

const base =
  "inline-flex items-center justify-center rounded-card font-medium transition-colors " +
  "focus:outline-none focus:ring-1 focus:ring-bleuGlacier disabled:opacity-60 disabled:cursor-not-allowed";

const variants: Record<string, string> = {
  primary:
    "bg-bleuMinistre hover:bg-bleuGlacier text-blancNordique shadow-carte",
  secondary:
    "bg-slate-800 hover:bg-slate-700 text-blancNordique border border-slate-600",
  ghost:
    "bg-transparent hover:bg-slate-800 text-blancNordique border border-transparent",
  danger:
    "bg-rougeErable hover:bg-red-700 text-blancNordique shadow-carte",
};

const sizes: Record<string, string> = {
  sm: "px-3 py-1 text-xs",
  md: "px-4 py-2 text-sm",
};

const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  className,
  ...props
}) => {
  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
};

export default Button;

