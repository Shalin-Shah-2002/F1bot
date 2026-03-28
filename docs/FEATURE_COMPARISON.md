# F1bot Feature Comparison vs Competitors

## Scope

This comparison maps **F1bot planned features** from `docs/FEATURES.md` against publicly advertised capabilities from:
- F5Bot
- Syften
- Awario
- Brand24
- Social Searcher
- BrandMentions
- Mention
- Brandwatch
- Talkwalker
- Meltwater

## Legend

- ✅ = Clearly advertised
- ◐ = Partial / plan-dependent / indirect
- — = Not clearly advertised

---

## Capability Matrix

| Capability | F1bot (Planned) | F5Bot | Syften | Awario | Brand24 | Social Searcher | BrandMentions | Mention | Brandwatch | Talkwalker | Meltwater |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Reddit monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ |
| Multi-source monitoring | ◐ (Phase 2+) | ◐ (3 sources) | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Real-time alerts | ◐ (Phase 2) | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| Advanced query/filtering | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ◐ | ✅ | ✅ | ✅ | ✅ |
| AI filtering / semantic analysis | ✅ | ✅ | ✅ | ◐ | ✅ | — | ✅ | ◐ | ✅ | ✅ | ✅ |
| Lead score + qualification reason | ✅ | — | — | — | — | — | — | — | — | — | — |
| Outreach suggestion generation | ✅ | — | — | ◐ | — | — | — | — | — | — | — |
| Lead status pipeline (`new/contacted/qualified/ignored`) | ✅ | — | — | — | — | — | — | — | — | — | — |
| CSV export for leads | ✅ | ◐ (feeds/API) | ◐ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ |
| API/Webhooks | ◐ (Phase 2+) | ✅ | ✅ | ✅ | ◐ | — | ◐ | ◐ | ✅ | ✅ | ✅ |
| Collaboration/team workflow | ◐ (Phase 3) | ◐ | ◐ | ◐ | ✅ | — | ◐ | ✅ | ✅ | ✅ | ✅ |
| Sentiment analytics | ◐ (future) | — | ◐ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| Scheduled automation/scans | ✅ (Phase 2) | ◐ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| CRM integrations | ✅ (Phase 3) | — | ◐ | ◐ | ◐ | — | ◐ | ◐ | ✅ | ✅ | ✅ |
| Influencer discovery | — | — | — | ✅ | ✅ | ◐ | ◐ | ◐ | ✅ | ◐ | ✅ |
| Social publishing/engagement inbox | — | — | — | ◐ | — | — | — | ✅ | ✅ | ◐ | ◐ |

---

## Where F1bot Is Strong (Differentiators)

1. **Lead-first workflow, not just monitoring**
   - Score + qualification reason + outreach suggestion in one pass.
2. **Reddit-first intent engine**
   - Optimized for high-intent discovery rather than broad social listening.
3. **Founder-friendly focus**
   - Lightweight pipeline (`new/contacted/qualified/ignored`) vs heavy enterprise suites.

---

## Where F1bot Is Behind (Gaps)

1. **Automation & distribution gaps**
   - Scheduled scans, alert routing, and webhooks are not fully shipped yet.
2. **Team and enterprise gaps**
   - Collaboration roles, approvals, and advanced reporting are behind enterprise tools.
3. **Ecosystem gaps**
   - Multi-source expansion and CRM integrations are later-phase features.

---

## Priority Roadmap to Compete Better

### Priority 1 (Immediate)
- Ship scheduled scans + alerting (email/Slack)
- Add webhook endpoint support
- Add stronger advanced filtering UI (boolean + subreddit-specific rule sets)

### Priority 2 (Near-term)
- Add sentiment + urgency overlays on lead cards
- Add API endpoints for export and external sync
- Improve lead inbox with saved views/filters

### Priority 3 (Growth)
- CRM integrations (HubSpot/Pipedrive/Notion)
- Team workspaces and role-based access
- Multi-source expansion beyond Reddit

---

## Practical Positioning Statement

**F1bot** should position itself as:

> "The fastest Reddit intent-to-outreach engine for founders and lean growth teams."

This avoids direct enterprise-platform competition while winning on speed, relevance, and conversion workflow.

---

## Notes

- Comparison is based on publicly advertised product pages and may vary by plan tier.
- Use this as a product strategy guide, not as legal/contractual feature verification.
