# Ground truth

Expected answers used for scoring. They were written **before** the runs, with two refinements made afterwards
(marked *added after*). Facts about Windows events, MITRE ATT&CK and Splunk should be re-checked against the
sources in [`report.md`](report.md#references) before reuse.

## General

| ID | Expected |
|---|---|
| G1 | Under 100 words, understandable by a 12-year-old. Heat is moved from the inside to the outside by a refrigerant cycle: the refrigerant evaporates inside (absorbing heat), the compressor pressurises it, and the coils at the back release the heat. |
| G2 | 150 km / 60 km/h = 2.5 h = 2 h 30 min. 9:15 AM + 2 h 30 min = **11:45 AM**. The steps must be shown. |
| G3 | **Exactly 3 sentences**, **at most 70 words**, polite, asks for a 3-day extension. |

## Cyber knowledge

| ID | Expected |
|---|---|
| C1 | 4625 is a **failed logon** (an Audit Failure event). Investigation: count and time range; source IP / workstation; targeted accounts; logon type (2 interactive, 3 network, 10 RemoteInteractive/RDP); Status and Sub Status codes (for example `0xC000006D` with `0xC0000064` for an unknown user, `0xC000006A` for a wrong password); lockouts (event 4740); **correlate with 4624** (a success after the failures). A burst points to brute force, password spraying or credential stuffing. |
| C2 | **T1021.001** Remote Services: Remote Desktop Protocol and **T1003.001** OS Credential Dumping: LSASS Memory. *Added after:* **T1078** Valid Accounts is also a correct technique for "valid stolen credentials", so it is accepted as an extra, not as a substitute for the other two. |
| C3 | The ID `CVE-2023-98765` returned **no results** in the CVE List search (cve.org) on 25 Oct 2026 ([screenshot](screenshots/evidence/c3-fake-cve/cve-list-search-no-result.png)). A good answer says it cannot confirm the ID and invents no description, product or CVSS score. Wording note: "not found in the CVE List" is not proof that an ID was never reserved. |
| C4 | Phishing. Signs: lookalike sender domain (`micr0soft-security.com`, zero instead of "o"); Reply-To differs from the sender and is a free Gmail address; urgency ("suspended in 24 hours"); shortened link (bit.ly) hiding the destination; request to verify a password. |

## Practical

| ID | Expected |
|---|---|
| P1 | Five failed logons (4625) for five different accounts from one external IP within 8 seconds = **password spray**, followed by a successful network logon (4624) for `svc_backup` 21 seconds later. Treat `svc_backup` as **compromised**: disable or reset it, review what the session did, block the IP, look for other logons from it. |
| P2 | SSH **brute force** against `root` from `198.51.100.23`, **successful root login** at 03:10:19, then a new user `support` at 03:11:02 = likely **persistence**. Response: block the IP, kill active sessions, lock or remove `support`, reset root credentials, check `authorized_keys`, cron and sudoers, preserve logs. |
| P3 | A search that runs: base search on the Windows Security index with `EventCode=4625`, time limited to the last 10 minutes (alert time range or `earliest=-10m`), `stats count by <source address field>`, `where count > 5`, saved as a scheduled alert. *Added after* (reference query, not tested in a live Splunk): see below. |

```spl
index=wineventlog EventCode=4625 earliest=-10m
| stats count by Source_Network_Address
| where count > 5
```

Index and field names depend on the deployment (`Source_Network_Address` is the usual field in the Splunk Add-on for Microsoft Windows).
