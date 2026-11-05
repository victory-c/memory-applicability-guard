# Structured examples

Each example supplies structured classifications; the prototype does not infer them from unrestricted natural language.

## 1. Superseded pool memory

Old memory: “The user previously trained at the downtown pool.” Current evidence: “The user has moved, and the old pool is no longer convenient.” Mark the old training record `MEMORY_SOURCE/decisive=false` and the move record `USER_STATEMENT/decisive=true`. Use `relationship=SUPERSEDED`, `permission=ALLOWED`, and proposed action `USE`. Result: `REVISE`, `CLEAR_INAPPLICABLE`, `IGNORE`; the move record is decisive.

## 2. Cross-domain no bridge

A personal climbing preference is proposed for team training without affirmative transfer evidence. Use `relationship=NO_BRIDGE`. Result: `IGNORE`; similarity between activities is not transfer permission.

## 3. Explicit transfer

The user explicitly states that the preference also applies to the team setting. Use `relationship=EXPLICIT_TRANSFER`, allowed permission, and sufficient evidence. Result: `CLEAR_APPLICABLE / USE`.

## 4. Permission revoked

Current permission evidence revokes an older authorization. Use `permission=REVOKED` even when the content remains relevant. Result: `CLEAR_INAPPLICABLE / IGNORE`.

## 5. User-resolvable uncertainty

The user's answer would change the action and no robust action exists. Use `evidence_status=USER_RESOLVABLE`. Result: `ASK_USER`, `UNCERTAIN / ASK`.

## 6. External real-time evidence

A remembered train delay, price, inventory, or live status needs current verification. Use `evidence_status=EXTERNAL_REQUIRED`. Result: `VERIFY_EXTERNAL`, `UNCERTAIN / IGNORE`; do not ask the user to guess.

## 7. Robust action

One supplied action is acceptable across the reasonable applicability worlds. Set `robust_action_available=true` and name it. Result: do not ASK; ignore the disputed memory and take the robust action.

## 8. High-risk unresolved case

Set `risk=HIGH`. Result: `ESCALATE`, `UNCERTAIN / IGNORE`. The prototype cannot autonomously approve high-risk memory-grounded actions.
