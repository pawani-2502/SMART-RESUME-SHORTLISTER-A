# Showcase Module — Detachable Presentation Layer

This folder is **completely isolated** from production application logic.

## Routes (thin wrappers in `frontend/src/app/`)

| Route | Entry |
|-------|-------|
| `/demo` | `showcase/demo/pages/ShowcaseDemoEntry.tsx` |
| `/demo?mode=quick` | 2-minute tour |
| `/demo?mode=examiner` | 5-minute full walkthrough |
| `/about` | `showcase/about/pages/AboutPage.tsx` |

## Architecture

```
showcase/
├── config/           # Demo modes, step metadata, developer info
├── sample-data/      # Static JSON — no API calls
├── walkthrough-engine/  # Reusable tour provider + hooks
├── shared/           # UI, animations, theme, styles
├── demo/             # Demo pages, steps, layouts
└── about/            # Marketing/portfolio page
```

## Data Flow

1. User opens `/demo?mode=examiner`
2. Thin Next.js page imports `ShowcaseDemoEntry`
3. `WalkthroughProvider` loads step IDs from config
4. All content reads from `showcase/sample-data/*.json`
5. **Zero** calls to backend APIs or database

## Detachability

To remove the showcase:

1. Delete the `showcase/` folder
2. Delete `frontend/src/app/demo/` and `frontend/src/app/about/`
3. Remove `@showcase/*` from `tsconfig.json` paths
4. Remove showcase from `tailwind.config.js` content array

Production dashboard, jobs, rankings, auth, and APIs remain fully functional.

## Dependencies

- `framer-motion` (added to frontend `package.json`)
- `recharts` (already in frontend)
- No backend dependencies
