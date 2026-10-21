# Architecture and checklist

```mermaid
flowchart LR
  UI[Next.js frontend\n(Checkpoint 3)] --> API[FastAPI backend]
  API --> DB[(PostgreSQL)]
  API --> Q[(Redis)]
  Q --> W[Celery worker]
  W --> DB
  W --> LX[LaTeX service\n(Checkpoint 2)]
  W --> SRC[Job sources\nAdzuna / Remotive / Greenhouse / Lever]
  W --> MAIL[SMTP / Resend]
  GHA[GitHub Actions cron\n(Checkpoint 5)] --> W
```

## Checklist
| # | Item | Status |
|---|------|--------|
| 1 | Repo, compose, env template, DB models + migration, health checks, CI | Written; NOT yet run (see README "Verification status") |
| 2 | Resume import, analysis, tailoring, sandboxed LaTeX compile | Pending (needs your LaTeX) |
| 3 | Frontend | Pending |
| 4 | Job sources, salary filter, dedup, matching | Pending |
| 5 | Email digest, GitHub Actions schedule, final report | Pending |

## Strict salary rule (implemented in Checkpoint 4)
`salary_status`: `qualified` only when verified annual INR **minimum > 1,500,000**.
Max-only above threshold = `uncertain`; missing/ambiguous = `unknown`. Exactly 15 LPA = `below`.
