# Historical enrichment

Status: **completed**
Adapter: local\_history
Queries: 8

These results describe historical presence, not a compromise verdict.

| Kind | Criteria | Outcome | Records | Complete search |
|---|---|---|---:|---|
| ip\_prevalence | \{&quot;endpoint\_ip&quot;: &quot;10\.0\.0\.1&quot;\} | seen | 1 | True |
| attribute\_prevalence | \{&quot;dst\_company&quot;: &quot;Example Network&quot;\} | seen | 2 | True |
| attribute\_prevalence | \{&quot;dst\_registered\_org&quot;: &quot;Example Registry Organization&quot;\} | seen | 2 | True |
| attribute\_prevalence | \{&quot;dst\_asn&quot;: 64512\} | seen | 2 | True |
| ip\_prevalence | \{&quot;endpoint\_ip&quot;: &quot;203\.0\.113\.10&quot;\} | seen | 2 | True |
| directed\_activity\_tuple | \{&quot;dst&quot;: &quot;203\.0\.113\.10&quot;, &quot;protocol&quot;: &quot;TCP&quot;, &quot;src&quot;: &quot;10\.0\.0\.1&quot;, &quot;src\_site&quot;: &quot;alpha&quot;\} | seen | 1 | True |
| domain\_prevalence | \{&quot;dst\_domain&quot;: &quot;transfer\.example&quot;\} | seen | 2 | True |
| attribute\_prevalence | \{&quot;dst\_country&quot;: &quot;ZZ&quot;\} | seen | 2 | True |

## Limitations

- Seen before does not establish benign activity or compromise\.
- Negative results apply only to declared complete history and the exact criteria/window\.
- Counts are matched records, not independent connections; incomplete counts are lower bounds\.
- Attribute prevalence does not establish that the same endpoint or behavior occurred\.
- IP prevalence is dataset\-wide; private IP reuse, NAT and DHCP require scoped interpretation\.
- V3 omits domains, related\-only indicators and full registration attributes\.
- Current input hypotheses are untrusted context and do not drive queries\.
