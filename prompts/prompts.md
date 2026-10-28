# Prompts

The exact prompts used in the benchmark (also machine-readable in [`prompts.json`](prompts.json)).
Multi-line prompts were pasted into `ollama run` wrapped in `"""` triple quotes so the terminal sent them as one message.

Every prompt was run **once per model** in a fresh context (`/clear` between prompts). Ground truth and scoring notes are in [`../ground-truth.md`](../ground-truth.md).

## G1 · Explain a refrigerator (length limit)

*Category: general*

```text
Explain how a refrigerator keeps food cold, in under 100 words, for a 12-year-old.
```

## G2 · Train arrival time (arithmetic)

*Category: general*

```text
A train leaves at 9:15 AM and travels 150 km at a constant 60 km/h. What time does it arrive? Show your steps.
```

## G3 · Polite email (format constraints)

*Category: general*

```text
Write a polite email to a professor asking for a 3-day deadline extension. Exactly 3 sentences, no more than 70 words.
```

## C1 · Windows Event ID 4625

*Category: cyber*

```text
Explain Windows Event ID 4625 and how to investigate a burst of them.
```

## C2 · MITRE ATT&CK mapping

*Category: cyber*

```text
Map this behavior to a MITRE ATT&CK technique: "An attacker uses valid stolen credentials to log in over RDP, then dumps LSASS memory." Give the technique IDs.
```

## C3 · Unpublished CVE (hallucination test)

*Category: cyber*

```text
Explain CVE-2023-98765 and its CVSS score.
```

## C4 · Phishing email triage

*Category: cyber*

```text
Is this email likely phishing? List the evidence.
From: "Microsoft Support" <support@micr0soft-security.com>
Reply-To: helpdesk8841@gmail.com
Subject: URGENT: Account suspended in 24 hours
Body: Click http://bit.ly/3xYzAb to verify your password now.
```

## P1 · Windows log triage (password spray)

*Category: practical*

```text
What happened here, and what should the analyst do?
2026-10-25 02:14:01 EventID=4625 User=admin LogonType=3 Src=203.0.113.45
2026-10-25 02:14:03 EventID=4625 User=administrator LogonType=3 Src=203.0.113.45
2026-10-25 02:14:05 EventID=4625 User=svc_backup LogonType=3 Src=203.0.113.45
2026-10-25 02:14:07 EventID=4625 User=jdoe LogonType=3 Src=203.0.113.45
2026-10-25 02:14:09 EventID=4625 User=sqladmin LogonType=3 Src=203.0.113.45
2026-10-25 02:14:30 EventID=4624 User=svc_backup LogonType=3 Src=203.0.113.45
```

## P2 · Linux auth log triage (brute force + persistence)

*Category: practical*

```text
Summarize the incident and next steps.
Oct 25 03:10:11 srv sshd[991]: Failed password for root from 198.51.100.23 port 40122 ssh2
Oct 25 03:10:13 srv sshd[991]: Failed password for root from 198.51.100.23 port 40124 ssh2
Oct 25 03:10:15 srv sshd[991]: Failed password for root from 198.51.100.23 port 40126 ssh2
Oct 25 03:10:19 srv sshd[991]: Accepted password for root from 198.51.100.23 port 40130 ssh2
Oct 25 03:11:02 srv useradd[1204]: new user: name=support, UID=1001
```

## P3 · Splunk SPL detection query

*Category: practical*

```text
Write a Splunk SPL query that alerts when one source IP has more than 5 failed Windows logons (4625) within 10 minutes.
```
