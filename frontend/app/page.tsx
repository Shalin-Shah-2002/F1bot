import Link from "next/link";

const FEATURE_ITEMS = [
  {
    title: "Intent Discovery",
    description: "Scans selected subreddits for conversations that match your business context and buyer language."
  },
  {
    title: "AI Lead Scoring",
    description: "Ranks opportunities with qualification reasoning and outreach suggestions to speed up prioritization."
  },
  {
    title: "Lead Inbox",
    description: "Review each lead in a focused workspace with status transitions for pipeline clarity."
  },
  {
    title: "Profile Context",
    description: "Define your product pitch, target keywords, and subreddits once and reuse across scans."
  },
  {
    title: "CSV Export",
    description: "Export filtered lead lists for CRM upload, outbound workflows, or analyst handoff."
  },
  {
    title: "Runtime Visibility",
    description: "View backend environment health, integrations, and scan limits directly in the dashboard."
  }
] as const;

const WORKFLOW_STEPS = [
  {
    title: "Set Targeting Profile",
    detail: "Capture your business offer, keywords, and niche communities in one profile."
  },
  {
    title: "Run Smart Scan",
    detail: "Trigger backend scan and gather high-intent Reddit posts with scoring metadata."
  },
  {
    title: "Qualify And Track",
    detail: "Move leads through new, contacted, qualified, and ignored stages with full context."
  },
  {
    title: "Export And Execute",
    detail: "Download CSV for outreach execution, reporting, and CRM synchronization."
  }
] as const;

const FAQ_ITEMS = [
  {
    question: "What does this project solve?",
    answer:
      "It solves manual Reddit prospecting by combining search, AI qualification, and lead workflow in one interface."
  },
  {
    question: "Can I use it without full production auth?",
    answer:
      "Yes. In local development, the backend supports a fallback auth mode for quick iteration and testing."
  },
  {
    question: "Who is this made for?",
    answer:
      "Growth teams, founders, and agencies that need repeatable social-signal lead generation with better prioritization."
  }
] as const;

export default function HomePage() {
  const year = new Date().getFullYear();

  return (
    <main className="landing-shell mx-auto w-full max-w-6xl px-6 pb-14 pt-6 md:pb-24 md:pt-8">
      <section className="brand-card relative mt-2 overflow-hidden p-6 md:p-9">
        <div className="pointer-events-none absolute -left-8 top-0 h-28 w-28 rounded-full bg-brand-gold/16 blur-xl" />
        <div className="pointer-events-none absolute -right-8 bottom-0 h-32 w-32 rounded-full bg-brand-orange/14 blur-xl" />

        <div className="relative grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">AI-ASSISTED REDDIT LEAD ENGINE</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-brand-burgundy md:text-6xl" style={{ fontFamily: "var(--font-fraunces)" }}>
              Build A High-Intent Prospect Pipeline From Real Conversations
            </h1>
            <p className="mt-4 max-w-2xl text-sm text-brand-navy/80 md:text-lg">
              F1bot helps teams identify buying intent on Reddit, rank leads with AI, and operate a clear follow-up workflow from one modern dashboard.
            </p>

            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link href="/register" className="brand-btn-primary px-5 py-3 text-sm md:text-base">
                Start Free Setup
              </Link>
              <Link href="/scan" className="brand-btn-secondary px-5 py-3 text-sm md:text-base">
                Try Scanner
              </Link>
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              <span className="brand-badge">FastAPI Backend</span>
              <span className="brand-badge">Gemini Scoring</span>
              <span className="brand-badge">Lead Status Workflow</span>
              <span className="brand-badge">CSV Export</span>
            </div>
          </div>

          <aside className="rounded-2xl border border-brand-navy/15 bg-white/72 p-5 shadow-md">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/75">Command Preview</p>
            <h2 className="mt-2 text-2xl font-semibold text-brand-navy" style={{ fontFamily: "var(--font-fraunces)" }}>
              From Signal To Action
            </h2>

            <div className="mt-4 grid gap-3">
              <div className="rounded-xl bg-white/80 p-3 ring-1 ring-brand-navy/12">
                <p className="text-xs uppercase tracking-[0.1em] text-brand-burgundy/70">Scan Input</p>
                <p className="mt-1 text-sm text-brand-navy/90">Business profile + keywords + target subreddits</p>
              </div>
              <div className="rounded-xl bg-white/80 p-3 ring-1 ring-brand-navy/12">
                <p className="text-xs uppercase tracking-[0.1em] text-brand-burgundy/70">AI Result</p>
                <p className="mt-1 text-sm text-brand-navy/90">Lead score + qualification reason + outreach idea</p>
              </div>
              <div className="rounded-xl bg-white/80 p-3 ring-1 ring-brand-navy/12">
                <p className="text-xs uppercase tracking-[0.1em] text-brand-burgundy/70">Execution</p>
                <p className="mt-1 text-sm text-brand-navy/90">Track status, review details, export filtered CSV</p>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="defer-section mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Average setup", value: "< 2 min" },
          { label: "Lead statuses", value: "4 workflow stages" },
          { label: "Export format", value: "CSV ready" },
          { label: "Pipeline style", value: "AI + human review" }
        ].map((stat) => (
          <article key={stat.label} className="brand-stat">
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/70">{stat.label}</p>
            <p className="mt-1 text-lg font-semibold text-brand-navy">{stat.value}</p>
          </article>
        ))}
      </section>

      <section id="about" className="defer-section mt-8 grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
        <article className="brand-card p-6 md:p-7">
          <p className="text-xs tracking-[0.2em] text-brand-burgundy/75">WHAT THIS PROJECT DOES</p>
          <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
            A Complete Reddit Lead Generation Workflow
          </h2>
          <p className="mt-4 text-sm text-brand-navy/85 md:text-base">
            This project combines discovery, scoring, pipeline management, and export into one product. Instead of manually scanning threads and guessing lead quality, your team gets a ranked queue with clear context and action suggestions.
          </p>
          <div className="mt-5 grid gap-3 text-sm text-brand-navy/88">
            <div className="rounded-xl border border-brand-navy/14 bg-white/76 px-4 py-3">
              Detect conversations where people express active need or purchase intent.
            </div>
            <div className="rounded-xl border border-brand-navy/14 bg-white/76 px-4 py-3">
              Use AI-assisted scoring to prioritize who to contact first.
            </div>
            <div className="rounded-xl border border-brand-navy/14 bg-white/76 px-4 py-3">
              Manage the lifecycle from discovery to qualified opportunity.
            </div>
          </div>
        </article>

        <article className="brand-card p-6 md:p-7">
          <p className="text-xs tracking-[0.2em] text-brand-burgundy/75">ARCHITECTURE SNAPSHOT</p>
          <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
            Designed For Reliable Operations
          </h2>
          <div className="mt-4 grid gap-3">
            {["Frontend dashboard", "FastAPI API", "Reddit + Gemini services", "Leads repository + CSV export"].map((item, index) => (
              <div key={item} className="rounded-xl bg-white/76 px-4 py-3 ring-1 ring-brand-navy/12">
                <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/65">Step {index + 1}</p>
                <p className="mt-1 text-sm font-medium text-brand-navy/90 md:text-base">{item}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section id="features" className="defer-section mt-8">
        <div className="mb-4 px-1">
          <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">FEATURES</p>
          <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy md:text-4xl" style={{ fontFamily: "var(--font-fraunces)" }}>
            Everything Needed For Social Lead Ops
          </h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {FEATURE_ITEMS.map((item) => (
            <article key={item.title} className="brand-card p-5">
              <h3 className="text-xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
                {item.title}
              </h3>
              <p className="mt-2 text-sm text-brand-navy/85 md:text-base">{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="workflow" className="defer-section brand-card mt-8 p-6 md:p-8">
        <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">WORKFLOW</p>
        <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy md:text-4xl" style={{ fontFamily: "var(--font-fraunces)" }}>
          Practical, Repeatable Process
        </h2>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {WORKFLOW_STEPS.map((step, index) => (
            <article key={step.title} className="rounded-2xl border border-brand-navy/14 bg-white/78 p-4">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-orange text-xs font-bold text-brand-cream">
                  {index + 1}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-brand-burgundy">{step.title}</h3>
                  <p className="mt-1 text-sm text-brand-navy/85">{step.detail}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="faq" className="defer-section brand-card mt-8 p-6 md:p-8">
        <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">FAQ</p>
        <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
          Common Questions
        </h2>

        <div className="mt-4 grid gap-3">
          {FAQ_ITEMS.map((item) => (
            <details key={item.question} className="rounded-xl bg-white/78 p-4 ring-1 ring-brand-navy/12">
              <summary className="cursor-pointer list-none text-base font-semibold text-brand-burgundy">{item.question}</summary>
              <p className="mt-2 text-sm text-brand-navy/85">{item.answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="defer-section brand-card mt-8 overflow-hidden p-6 md:p-8">
        <div className="grid items-center gap-6 md:grid-cols-[1fr_auto]">
          <div>
            <p className="text-xs tracking-[0.24em] text-brand-burgundy/80">READY TO DEPLOY</p>
            <h2 className="mt-2 text-3xl font-semibold text-brand-burgundy md:text-4xl" style={{ fontFamily: "var(--font-fraunces)" }}>
              Launch Your Lead Workflow
            </h2>
            <p className="mt-3 max-w-2xl text-sm text-brand-navy/80 md:text-base">
              Start with your profile, run a scan, and move from social signal to qualified pipeline faster.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/register" className="brand-btn-primary px-5 py-3 text-sm">
              Create Account
            </Link>
            <Link href="/login" className="brand-btn-secondary px-5 py-3 text-sm">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      <footer className="defer-section brand-card mt-8 p-5 md:p-6">
        <div className="grid gap-5 md:grid-cols-[1.2fr_0.8fr_0.8fr]">
          <div>
            <h3 className="text-2xl font-semibold text-brand-burgundy" style={{ fontFamily: "var(--font-fraunces)" }}>
              F1bot
            </h3>
            <p className="mt-2 text-sm text-brand-navy/82">
              AI-powered Reddit lead generation platform for founders, agencies, and growth teams.
            </p>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/75">Product</p>
            <div className="mt-2 grid gap-1.5 text-sm text-brand-navy/85">
              <Link href="/scan" className="hover:text-brand-burgundy">Scanner</Link>
              <Link href="/leads" className="hover:text-brand-burgundy">Leads Inbox</Link>
              <Link href="/export" className="hover:text-brand-burgundy">Export</Link>
              <Link href="/settings" className="hover:text-brand-burgundy">Settings</Link>
            </div>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-brand-burgundy/75">Account</p>
            <div className="mt-2 grid gap-1.5 text-sm text-brand-navy/85">
              <Link href="/register" className="hover:text-brand-burgundy">Create Account</Link>
              <Link href="/login" className="hover:text-brand-burgundy">Login</Link>
              <a href="#faq" className="hover:text-brand-burgundy">Support FAQ</a>
            </div>
          </div>
        </div>

        <div className="mt-6 border-t border-brand-navy/12 pt-4 text-xs tracking-[0.12em] text-brand-navy/65">
          © {year} F1bot. Built for practical lead operations.
        </div>
      </footer>
    </main>
  );
}
