# Security

- Never commit `.env`, API keys, resumes, or generated PDFs (see `.gitignore`).
- Keep the repository **private** if it contains personal data.
- Job descriptions and imported documents are untrusted input. They must never
  be executed or allowed to override resume-integrity rules.
- LaTeX compilation (Checkpoint 2) runs in an isolated container with
  `-no-shell-escape`, time/memory/size limits.
- Report vulnerabilities privately to the repository owner.
