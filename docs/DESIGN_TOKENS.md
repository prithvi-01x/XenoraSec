# Design Tokens & Style Guide

A specification of design tokens, color ramps, typography weights, and UI components across XenoraSec.

## Colors & Palette

```css
--color-background: #090d16;
--color-surface: #0e1526;
--color-surface-light: #162035;
--color-surface-border: #1e2c47;

--color-primary: #2563eb;
--color-primary-hover: #1d4ed8;
--color-primary-light: #3b82f6;
--color-accent: #0ea5e9;

--color-success: #10b981;
--color-danger: #ef4444;
--color-warning: #f59e0b;
--color-info: #64748b;
```

## Severity Tokens

| Severity | Text Class | Background Class | Border Class |
|----------|------------|------------------|--------------|
| `critical` | `text-red-400` | `bg-red-950/60` | `border-red-800/80` |
| `high` | `text-orange-400` | `bg-orange-950/60` | `border-orange-800/80` |
| `medium` | `text-amber-300` | `bg-amber-950/60` | `border-amber-800/80` |
| `low` | `text-emerald-400` | `bg-emerald-950/60` | `border-emerald-800/80` |
| `info` | `text-slate-400` | `bg-slate-900/80` | `border-slate-700/80` |
