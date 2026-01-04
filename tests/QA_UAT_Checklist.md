# ✅ TSA Chatbot Validation – Test Questions Checklist

## 1️⃣ Greeting & Main Menu Validation
1. Does the chatbot always show the **welcome message + service list** on first message?
2. Does it clearly explain **what services it can provide**?
3. Does the menu appear even if the user types: “hi”, “hello”, “test”?
4. Are menu numbers (0–9) accepted correctly?
5. Does entering an **invalid number (e.g., 11 or -1)** return a friendly error?
6. After “Exit Chat (0)”, does the session reset properly?

## 2️⃣ Menu Navigation & Flow Control
7. Can the user always return to the **Previous Menu**?
8. Does the chatbot remember the **current menu context**?
9. If the user types free text instead of a number, does it understand intent OR ask them to choose?
10. Does the chatbot prevent users from jumping to unrelated flows?

## 3️⃣ Player Registration & Venue Details
**Phone Number Flow**
11. When I enter a **valid phone number**, does it fetch registration details?
12. If there is **only one registration**, does it directly return Venue, Date, Sport?
13. If there are **multiple registrations**, does it List all sports and Ask for Ack No?
14. What happens if the phone number: Has spaces? Has +91 prefix? Is incomplete?

**Acknowledgment Number Flow**
15. Does searching by **Ack Number** return full details?
16. Are **player name, village, mandal, district** correct?
17. Does it correctly show **selection status** (Mandal/District/State)?

**Fallback Handling**
18. If venue is not assigned, does it show cluster incharge name/mobile?
19. If cluster data is missing in SQL, does RAG fallback work?

## 4️⃣ Privacy & Security Guardrails
20. If a user shares a phone number **without asking for venue**, does the bot warn about privacy?
21. Does the bot avoid repeating personal data unnecessarily?
22. Does it block or redact sensitive identifiers?
23. Does it clearly guide the user on **why data is needed**?

## 5️⃣ Match Schedules & Fixtures
24. Does “Cricket schedule” return the **next 5 matches**?
25. Are match details accurate (Teams, Time, Venue)?
26. Does “Mandal level schedule” return **static date ranges**?
27. Does “Match ID 123” return **only one specific match**?
28. What happens if Match ID does not exist or Sport is misspelled?

## 6️⃣ Selection Status & Results
29. Does the bot correctly differentiate Selected / Not Selected / Awaiting?
30. If selected, does it show Next level, Venue, Date?
31. Does it prevent showing results **before official announcement dates**?

## 7️⃣ Rules, Eligibility & FAQs (RAG + SQL)
32. Does “Age limit for Kabaddi” return the correct rule?
33. Does it differentiate rules **sport-wise**?
34. Are answers sourced correctly (SQL vs RAG)?
35. Does it answer “Will food be provided?” correctly?
36. Does it handle **out-of-scope questions** politely?

## 8️⃣ Statistics & Data Accuracy
37. Does “How many players registered?” fetch **real-time SQL count**?
38. Are sport-wise participation numbers correct?
39. Does it list sports at Mandal/District level?
40. Are stats consistent across multiple queries?

## 9️⃣ Location Intelligence
41. Does “Is Peddapalli a district?” return correct hierarchy?
42. Can it handle Villages, Mandals, Districts?
43. Does it clearly say when a location **does not exist**?
44. Does it avoid hallucinating new locations?

## 🔟 Downloads & Utilities
45. Does “Download acknowledgment” provide a valid official link?
46. Are portal URLs correct and active?
47. Does it block invalid or outdated events (e.g., “CM Cup 2015”)?
48. Does it explain **data availability limits clearly**?

## 1️⃣1️⃣ Multilingual & UX Checks
49. Does the bot auto-detect Telugu, Hindi, English?
50. Does language remain consistent across the session?
51. Does switching language via menu work instantly?
52. Are translations accurate?

## 1️⃣2️⃣ Technical & System Behavior
53. Does the bot correctly decide SQL vs RAG?
54. Does session memory work across follow-up questions?
55. Are responses tagged with source?
56. Does the bot fail gracefully if SQL is down?
57. Does it avoid repeating the same answer unnecessarily?

## 1️⃣3️⃣ Error Handling & Edge Cases
58. What happens if User pastes junk text or emojis?
59. Does the bot handle long messages?
60. Does it avoid infinite loops?
61. Does it recover from partial inputs?

## 1️⃣4️⃣ Performance & Scalability
62. Is response time acceptable?
63. Does menu rendering delay?
64. Behavior across Web/WhatsApp/Mobile?

## 1️⃣5️⃣ Final Acceptance Criteria
65. First-time user understanding <30s?
66. Parent venue check easy?
67. Coach data extraction fast?
68. Reduced helpdesk load?
69. Critical journeys automated?
