# Cross — Licensing Strategy

## Current license: MIT

Cross is released under the **MIT License**. This is the most permissive and
widely adopted open-source license. Anyone can use, modify, distribute, or build
on Cross without restriction, provided the copyright notice is retained.

See [LICENSE](LICENSE) for the full text.

---

## Why MIT at launch

License choice directly impacts adoption. For a new project with no user base,
**adoption is the bottleneck** — not monetization. You cannot sell licenses or
consulting to a project nobody has heard of.

MIT removes all friction:
- Individuals adopt without asking permission
- Companies can use it internally without a legal review
- Developers contribute without IP concerns
- GitHub, PyPI, and package managers treat MIT as a green light

The projects with the largest communities — React, Node.js, Vue.js, jQuery,
Rails, .NET Core, VS Code — are all MIT. Apache 2.0 is the runner-up for
enterprise-focused projects (Kubernetes, Android, Swift) because it adds
explicit patent protection that large company legal teams prefer.

---

## The monetization opportunity is real — MIT does not close the door

### The MySQL / Red Hat model

MySQL was GPL (free open source) for years. It built massive adoption, then sold
to Sun Microsystems for $1 billion. Red Hat built a $34 billion business entirely
on services around GPL Linux — never owning the kernel, just the expertise.

The open-source version *is* the product that creates the value. The license
does not determine whether money can be made — the **expertise, support, and
relationships** do.

### How Cross can follow this path

| Stage | What happens |
|---|---|
| **Now** | MIT license, broad adoption, GitHub stars, word of mouth |
| **Traction** | A developer at a news org / government agency / consultancy finds Cross |
| **Interest** | They show their team; it solves a real problem at scale |
| **Conversation** | They want deployment help, integration, or a support agreement → they call you |
| **Revenue** | Consulting fee, support contract, or custom development agreement |
| **Scale** | A company wants to embed Cross in their product → source license + ongoing consulting |

The `COMMERCIAL_LICENSE.md` file in this repo signals intent — it tells
organizations that commercial deployment invites a conversation, without
blocking anyone from using the software today.

---

## License evolution roadmap

### Phase 1 — Now (MIT)
Maximum adoption. Zero friction. Build the user base.
`COMMERCIAL_LICENSE.md` signals commercial intent without legal restriction.

### Phase 2 — At first commercial traction
Add a formal dual-license option:
- **Free tier:** MIT (unchanged — all existing users unaffected)
- **Commercial tier:** Separate written agreement for organizational deployment

This is the **MySQL / Qt model**. The free version keeps the community growing.
The commercial license generates revenue from organizations that need a vendor
relationship anyway (for procurement, support SLAs, or liability reasons).

### Phase 3 — If a company wants to embed or white-label Cross
Negotiate a **source license + consulting agreement**:
- One-time or annual license fee for embedding Cross in their product
- Consulting engagement for integration, customization, and training
- This is the scenario with the largest single-transaction revenue potential

### Phase 4 — Optional: BSL with open-source conversion
If the project reaches significant scale and competition becomes a concern,
consider **Business Source License (BSL 1.1)** on new versions:
- Free for non-production use
- Commercial use requires a license
- Automatically converts to MIT after 4 years
- Used by HashiCorp (Terraform), MariaDB, Sentry

**Caution:** HashiCorp's switch from MIT to BSL caused the community to fork
Terraform as OpenTofu. Only make this move if the project is large enough that
the fork risk is manageable.

---

## Licenses considered and why they were not chosen at launch

| License | Reason not chosen |
|---|---|
| **PolyForm Noncommercial** | Restricts commercial use immediately — kills adoption before community exists |
| **GPL v2** | Viral — any software that includes Cross must also be GPL; deters commercial integration |
| **BSL 1.1** | Designed for projects with existing user bases; triggers negative community reaction at launch |
| **ELv2 (Elastic)** | Only restricts managed/SaaS use — too narrow; doesn't cover consulting opportunity |
| **SSPL** | Extremely aggressive; would deter all enterprise interest |
| **Apache 2.0** | Good alternative to MIT; adds patent grant. Could switch to this if enterprise/government adoption becomes primary focus |

---

## Key principle

> The goal at launch is to get Cross into as many hands as possible.
> A project with 10,000 users and an MIT license is worth infinitely more
> than a project with 10 users and a restrictive license.
> Monetization follows traction — it does not precede it.

---

## The Linux kernel: GPL v2

The Linux kernel is licensed under **GNU GPL version 2 only** (Linus Torvalds
has stated he will never move to v3). Key lessons from Linux:

- The license did not prevent massive commercial success
- Red Hat, Canonical, SUSE, Google (Android), Amazon (AWS), and Microsoft (Azure)
  all built multi-billion dollar businesses on GPL Linux
- None of them own the kernel — they own the **expertise, support, and services**
- Government agencies worldwide use Linux freely — and pay for support contracts

The lesson: **a permissive or copyleft license does not prevent monetization.
It prevents control. Control is not required to make money.**

---

## Action items

- [x] T-13 LICENSE file created — MIT, 2026 ✓ 2026-03-05
- [x] COMMERCIAL_LICENSE.md created — signals commercial intent ✓ 2026-03-05
- [ ] Add your name/email to LICENSE copyright line and COMMERCIAL_LICENSE.md contact section
- [ ] Add MIT license badge to README.md: `[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)`
- [ ] Revisit license at 100 GitHub stars — evaluate dual-license transition

