# 📊 Eco-Sync: Hackathon Presentation Deck

## Slide 1: Title Slide
**Title:** Eco-Sync
**Subtitle:** AI-Driven Circular Barter Agent
**Footer:** Team Name | Hackathon 2025

**Visual:** Eco-Sync Logo (Purple Gradient Earth with Recycling Arrows)

---

## Slide 2: The Problem
**Header:** Campus Waste is a Coordination Problem
- **70%** of semester-end items (books, lab coats, drafters) are discarded or stored unused.
- **Why?** Finding the right person to swap with is time-consuming.
- **Current Solution:** Chaotic WhatsApp groups & notice boards.
- **The Gap:** A has X and wants Y. B has Y but wants Z. Direct swaps fail.

---

## Slide 3: The Solution: Eco-Sync
**Header:** Autonomous Multi-Party Barter Agent
**Core Concept:** An AI agent that "sees" items and orchestrates the market.

**Three Pillars:**
1.  **AI Vision:** Instant item recognition (Gemini).
2.  **Smart Matching:** Solves the "Double Coincidence of Wants" via graph cycles.
3.  **Gamification:** Eco-Credits drive behavior.

---

## Slide 4: How It Works (The Tech)
**Header:** Under the Hood

**1. Vision Layer (Gemini Pro Vision)**
   - user uploads photo ➜ JSON (Name, Category, Condition, Specs)

**2. Matching Engine (Graph Algorithms)**
   - Nodes = Users, Edges = Wants
   - Detects cycles: A ➜ B ➜ C ➜ A
   - Prioritizes: Department > Semester > Hostel

**3. Execution Layer (FastAPI)**
   - Atomic transactions
   - Real-time status updates

---

## Slide 5: Live Demo
**Header:** Let's See It In Action (3-Way Swap)

*(Switch to Live Demo)*

**Scenario:**
- **Arun** needs a Textbook (Has Drafter)
- **Priya** needs a Lab Coat (Has Textbook)
- **Ravi** needs a Drafter (Has Lab Coat)

**Result:** Eco-Sync detects the invisible cycle and orchestrates the swap instantly.

---

## Slide 6: Business Model & Impact
**Header:** Sustainability as a Service

**Impact Metrics:**
- Waste diverted from landfills
- Student money saved (avg. $500/semester)
- Carbon footprint reduction

**Gamification:**
- Leaderboards for top recyclers
- Redeem Eco-Credits for campus perks (coffee, printing)

---

## Slide 7: Future Roadmap
**Header:** Beyond the MVP

- **Phase 2:** Logistics integration (Campus delivery runners)
- **Phase 3:** Blockchain verification for Eco-Credits
- **Phase 4:** Expansion to inter-university swaps

---

## Slide 8: Summary
**Header:** Why Eco-Sync Wins

✅ **AI-Native:** Vision & Graph Agents
✅ **Solved Complexity:** Handles N-party swaps
✅ **Ready to Scale:** Stateless backend architecture

**Thank You!**
*Q&A*
