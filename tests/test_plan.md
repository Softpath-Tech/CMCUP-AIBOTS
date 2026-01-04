# Chatbot Verification Test Plan

## 1. Main Menu Navigation
- **Goal**: Ensure all 9 main menu options load their respective sub-menus.
- **Inputs**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
- **Expected**: Unique and correct menu text for each.

## 2. Schedule Flow (Fixed)
- **Goal**: Verify context persistence for "Schedule by Sport".
- **Steps**: Main -> 2 -> 1 -> "Kabaddi"
- **Expected**: "Kabaddi Schedule" (or "No schedule found for Kabaddi").
- **Anti-Pattern**: Generic "Welcome" or RAG answer unrelated to schedule.

## 3. Rules Flow (Fixed)
- **Goal**: Verify context persistence for "Age Limit".
- **Steps**: Main -> 4 -> 1 -> "Judo"
- **Expected**: "Rules for Judo" (RAG response specific to age/eligibility).

## 4. Location Flow
- **Goal**: Verify location lookup from menu prompt.
- **Steps**: Main -> 7 -> "Medipally"
- **Expected**: Location details for Medipally (via SQL).

## 5. Sub-Menu "Back" functionality
- **Goal**: Ensure "Back" returns to Main Menu from every sub-menu.
- **Steps**: Main -> [Any] -> Back -> Main.

## 6. Registration Flow
- **Goal**: Verify Phone lookup.
- **Steps**: Main -> 1 -> 1 -> "9848012345"
- **Expected**: "No registrations found" (or details if mock data exists) OR Privacy Warning if logic triggers.

## 7. Helpdesk & Downloads
- **Goal**: Verify static information.
- **Steps**: Main -> 8 -> 1; Main -> 6 -> 1.
- **Expected**: Static text with links/numbers.
