# FloodSense Severity Annotation Guidelines & Dataset Strategy

## 1. Overview and Purpose
This document establishes the official annotation guidelines for categorizing flood emergency communications into four distinct operational severity levels: **Low**, **Moderate**, **High**, and **Critical**.

In the FloodSense architecture:
- **Severity** reflects the acute threat to human life, bodily integrity, and essential safety.
- **HumAID Categories** (e.g., `requests_or_urgent_needs`, `rescue_volunteering_or_donation_effort`) reflect *humanitarian communication types*, which serve as contextual signals but must **not** be equated 1:1 with severity.

---

## 2. Severity Classification Schema

### Level 4: Critical (Life-Threatening Emergency)
* **Definition:** An immediate, acute threat to human life or survival requiring urgent life-saving rescue or immediate medical intervention.
* **Inclusion Criteria:**
  - People actively trapped, stranded, or marooned in rising water (e.g., trapped on rooftops, inside submerged houses, in vehicles swept away).
  - Active drowning or people in peril of being swept away.
  - Acute medical emergencies in isolated flood zones (e.g., oxygen depletion, dialysis patients cut off, critical injury).
  - Stranded vulnerable populations (infants, unaccompanied children, bedridden elderly, hospital patients) in direct contact with rising floodwaters.
* **Exclusion Criteria:**
  - Evacuations that were completed safely prior to inundation without trapped persons.
  - General food/water requests where physical safety is not immediately compromised.

### Level 3: High (Major Danger & Disruption)
* **Definition:** Rapidly worsening flood conditions or severe physical disruption that threatens safety, property, and access, but without confirmed life entrapment at the exact moment of reporting.
* **Inclusion Criteria:**
  - Floodwaters actively entering residential homes, commercial facilities, or public shelters.
  - Mandatory evacuation orders issued or in progress due to rapidly rising levels.
  - Major infrastructure collapse cutting off communities (e.g., dam breach/overflow, collapsed primary bridges, submerged major transit arteries).
  - Complete utility collapse (widespread power, drinking water, and communications outage) across flooded residential zones.
* **Exclusion Criteria:**
  - Water pooling on roads without ingress into structures or complete access blockage.
  - Long-term economic relief appeals without immediate structural danger.

### Level 2: Moderate (Advisory, Warnings & Property Impact)
* **Definition:** Measurable localized flooding, minor property water damage, or precautionary advisories without imminent threat to life or severe residential inundation.
* **Inclusion Criteria:**
  - Localized street waterlogging, impassable secondary streets, and municipal drainage overflow.
  - Precautionary flood watches, meteorological warnings, and official guidance.
  - Disruption of non-critical services (e.g., school closures, delayed transit routes).
  - General calls for volunteer relief supplies, donation collections, and post-flood sanitation efforts.
* **Exclusion Criteria:**
  - Pure weather forecasts without localized flood impact.
  - Messages conveying solely emotional support or condolences.

### Level 1: Low (Informational & Recovery Context)
* **Definition:** General humanitarian context, sympathy, weather observations, or historical commentary conveying no immediate emergency hazard.
* **Inclusion Criteria:**
  - Expressions of sympathy, prayers, condolences, and emotional solidarity.
  - Retrospective historical analyses of past flood events (e.g., *"remembering the 2018 floods"*).
  - General disaster news updates without immediate actionable threat.
  - Negations confirming safety (e.g., *"water levels receded, situation normal"*).

---

## 3. Disambiguation & Context-Aware Rules

1. **Negation Rule:** If an otherwise high-risk phrase is explicitly negated (e.g., *"no casualties reported"*, *"we are not trapped"*), the severity must be downgraded accordingly (to Low or Moderate).
2. **Hypothetical & Speculative Rule:** Messages expressing hypothetical scenarios (e.g., *"if the dam bursts we are in trouble"*) or unverified rumors must not be escalated to Critical unless accompanied by verified present-tense observations.
3. **Historical / Temporal Rule:** References to historical flood years or past casualties must not trigger Critical/High severity. The emergency must be active and present.
4. **Multi-Aspect Messages:** When a message contains elements spanning multiple levels (e.g., waterlogging on roads + 2 families trapped inside a house), **classify according to the highest-risk active element** (Critical).

---

## 4. Strategy for Obtaining a Reliable Ground-Truth Dataset

Because HumAID only provides communication topic labels, a rigorous ground-truth dataset for severity classification must be created through an independent, multi-annotator process:

### A. Sampling Strategy
1. **Source Corpus:** Extract a representative stratified sample of 1,500 flood messages:
   - 1,000 from the flood-specific HumAID splits (spanning all 10 categories to capture diverse language).
   - 500 from broader disaster repositories (e.g., CrisisLexT26, Disaster Response Data).
2. **Stratification:** Stratified by keyword patterns (water dynamics, life threat, damage, generic) to prevent class starvation in the Critical and High tiers.

### B. Multi-Annotator Protocol
1. **Annotator Qualifications:** Annotators must complete a qualification calibration test of 20 benchmark tweets with established gold labels, requiring $\ge 85\%$ accuracy to participate.
2. **Redundant Labeling:** Each message must receive independent judgments from **three separate annotators**.
3. **Inter-Annotator Agreement (IAA):**
   - Measure agreement using **Cohen's Kappa ($\kappa$)** for pairwise agreement and **Krippendorff's Alpha ($\alpha$)** for multi-annotator ordinal reliability.
   - Target minimum threshold: $\alpha \ge 0.75$.
4. **Adjudication Process:**
   - Any sample where annotators disagree across non-adjacent categories (e.g., Low vs Critical) must be escalated to an expert emergency management adjudicator.
   - The final dataset must preserve the individual annotator votes to allow uncertainty-aware evaluation.
