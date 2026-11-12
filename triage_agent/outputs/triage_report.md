# Alert triage report

Run: completed; 17 accepted findings; 7 groups; 0 narrative failures.

Investigation leads only. Supplied company/country labels are unverified; scores are not probabilities of compromise.

POC assumption: bytes_sent and bytes_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent.

## HIGH: 197.43.113.112
Incident: external\_service:197.43.113.112@2026-11-03T15:15:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fan\_in: 26.0 distinct internal sources; baseline mean 1.9375; z-score 29.1032644217105. Finding 0a933e27-0efd-418f-9dd5-4f7c44796a42.
- Supplied sample: 10 unique exact rows from 10 occurrences; 10 sources; 1 destinations; sent-byte sample sum 559693 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.28.142 | 197.43.113.112 | TCP | 78583 | 618088 | CANADA | DIGITALOCEAN LLC | Spoonbridge & Cherry | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[0\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.10.167 | 197.43.113.112 | TCP | 2214 | 8564786 | CANADA | DIGITALOCEAN LLC | Mississippi | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[1\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.144.164 | 197.43.113.112 | TCP | 72366 | 7777928 | CANADA | DIGITALOCEAN LLC | Nicollet Island | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[2\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.244.158 | 197.43.113.112 | TCP | 55040 | 8469428 | CANADA | DIGITALOCEAN LLC | Minnehaha | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[3\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.154.170 | 197.43.113.112 | TCP | 58147 | 74787 | CANADA | DIGITALOCEAN LLC | Nicollet Island | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[4\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 192.168.37.182 | 197.43.113.112 | TCP | 84817 | 3510667 | CANADA | DIGITALOCEAN LLC | Spoonbridge & Cherry | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[5\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 10.10.179.145 | 197.43.113.112 | TCP | 72417 | 1976502 | CANADA | DIGITALOCEAN LLC | Spoonbridge & Cherry | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[6\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 10.10.17.213 | 197.43.113.112 | TCP | 85379 | 4350618 | CANADA | DIGITALOCEAN LLC | Mississippi | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[7\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 10.10.74.206 | 197.43.113.112 | TCP | 24716 | 6136373 | CANADA | DIGITALOCEAN LLC | Lake Minnetonka | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[8\] \(source 14\) |
| 2026-11-03T15:15:00+00:00 → 2026-11-03T15:29:59.999000+00:00 | 10.10.160.17 | 197.43.113.112 | TCP | 26014 | 5966863 | CANADA | DIGITALOCEAN LLC | Mississippi | 0a933e27-0efd-418f-9dd5-4f7c44796a42:evidence\[9\] \(source 14\) |

### Highlighted indicators
- 10.10.160.17: source, related; supplied unverified labels: unknown
- 10.10.17.213: source, related; supplied unverified labels: unknown
- 10.10.179.145: source, related; supplied unverified labels: unknown

### Key evidence
- Detector-reported observation retained. \[0a933e27-0efd-418f-9dd5-4f7c44796a42:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## HIGH: 10.10.205.219
Incident: host:10.10.205.219@2026-11-03T15:45:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fanout: 34.0 distinct external destinations; baseline mean 5.9375; z-score 17.98880515082684. Finding 980ce573-9b5b-4390-ab92-c6fe7bec4db3.
- protocol\_mix: 31.0 distinct destinations over one protocol; baseline mean 1.5625; z-score 59.34042226244867. Finding e32912f6-2b75-4fd6-9194-e020cdb79325.
- Supplied sample: 11 unique exact rows from 20 occurrences; 1 sources; 11 destinations; sent-byte sample sum 330319 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 115.235.73.45 | UDP | 295 | 3167453 | IRELAND | ALIBABA CLOUD | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[0\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[0\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 173.12.169.76 | UDP | 724 | 965020 | UNITED STATES | CLOUDFLARE INC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[1\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[1\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 142.223.124.128 | UDP | 1199 | 7831540 | JAPAN | AMAZON.COM INC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[2\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[2\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 212.204.166.103 | UDP | 638 | 8354208 | JAPAN | CLOUDFLARE INC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[3\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[3\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 25.215.15.51 | UDP | 794 | 9415305 | NETHERLANDS | DIGITALOCEAN LLC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[4\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[4\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 66.83.99.99 | TCP | 323425 | 4622015 | FRANCE | LINODE LLC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[5\] \(source 16\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 28.97.75.144 | UDP | 216 | 8549294 | UNITED KINGDOM | TENCENT CLOUD | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[6\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[5\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 43.61.60.40 | UDP | 1457 | 303207 | UNITED STATES | ORACLE CORP | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[7\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[6\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 169.174.60.133 | UDP | 601 | 2582904 | CANADA | FASTLY INC | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[8\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[7\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 58.204.36.59 | UDP | 662 | 4741868 | UNITED KINGDOM | TENCENT CLOUD | Lake Minnetonka | 980ce573-9b5b-4390-ab92-c6fe7bec4db3:evidence\[9\] \(source 16\); e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[8\] \(source 17\) |
| 2026-11-03T15:45:00+00:00 → 2026-11-03T15:59:59.999000+00:00 | 10.10.205.219 | 30.167.238.4 | UDP | 308 | 3809551 | INDIA | OVH SAS | Lake Minnetonka | e32912f6-2b75-4fd6-9194-e020cdb79325:evidence\[9\] \(source 17\) |

### Highlighted indicators
- 10.10.205.219: entity, source; supplied unverified labels: unknown
- 115.235.73.45: destination, related; supplied unverified labels: company=ALIBABA CLOUD, country=IRELAND
- 142.223.124.128: destination, related; supplied unverified labels: company=AMAZON.COM INC, country=JAPAN

### Key evidence
- Detector-reported observation retained. \[980ce573-9b5b-4390-ab92-c6fe7bec4db3:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## HIGH: 192.168.213.37
Incident: host:192.168.213.37@2026-11-03T14:45:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fanout: 152.0 distinct external destinations; baseline mean 2.9375; z-score 95.55300731563922. Finding bd3f989d-0569-4cd3-bda1-052d5b310943.
- geo\_spread: 20.0 distinct destination countries; baseline mean 2.625; z-score 12.742109108692137. Finding cf01ec94-ef3d-475c-a53d-f96ae7f8b486.
- company\_spread: 20.0 distinct destination companies; baseline mean 2.3125; z-score 16.047457752601918. Finding 47b842b9-6243-4a8e-9873-422fa70a0648.
- protocol\_mix: 152.0 distinct destinations over one protocol; baseline mean 2.9375; z-score 95.55300731563922. Finding a026a35a-cbdb-4416-a49f-2c18d1bd0d48.
- Supplied sample: 25 unique exact rows from 40 occurrences; 1 sources; 25 destinations; sent-byte sample sum 702946 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 178.5.151.237 | TCP | 357 | 8307727 | JAPAN | CHOOPA LLC | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[0\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[0\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 220.83.242.43 | TCP | 63 | 7854589 | RUSSIA | GOOGLE LLC | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[1\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[1\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 161.84.194.247 | TCP | 367 | 104115 | BRAZIL | OVH SAS | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[2\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[2\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 4.5.106.76 | TCP | 226 | 1633839 | SWEDEN | GOOGLE LLC | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[3\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[3\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 7.136.87.228 | TCP | 252 | 8662906 | BRAZIL | LINODE LLC | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[4\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[4\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 166.202.168.162 | TCP | 109 | 6050148 | RUSSIA | M247 LTD | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[5\] \(source 6\); 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[0\] \(source 8\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[5\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 215.57.48.92 | TCP | 229 | 7834733 | BRAZIL | ALIBABA CLOUD | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[6\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[6\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 171.58.82.231 | TCP | 132 | 5522176 | GERMANY | AKAMAI TECHNOLOGIES | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[7\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[7\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 41.185.218.175 | TCP | 353 | 5304521 | NORTH KOREA | TENCENT CLOUD | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[8\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[8\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 162.80.36.139 | TCP | 47 | 2173523 | NORTH KOREA | SELECTEL | Minnehaha | bd3f989d-0569-4cd3-bda1-052d5b310943:evidence\[9\] \(source 6\); a026a35a-cbdb-4416-a49f-2c18d1bd0d48:evidence\[9\] \(source 9\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 177.141.109.206 | TCP | 310 | 9197801 | SWEDEN | SELECTEL | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[0\] \(source 7\); 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[4\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 68.100.1.150 | TCP | 101 | 7938211 | AUSTRALIA | AKAMAI TECHNOLOGIES | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[1\] \(source 7\); 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[2\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 58.198.93.16 | TCP | 392 | 7310945 | CANADA | LIDEN DATA INTERNETWORK AB | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[2\] \(source 7\); 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[9\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 27.44.70.191 | TCP | 139 | 4326210 | IRELAND | LIDEN DATA INTERNETWORK AB | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[3\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 202.206.99.113 | TCP | 69 | 4243411 | UNITED STATES | ORACLE CORP | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[4\] \(source 7\); 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[7\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 3.209.158.199 | TCP | 399 | 7863240 | VIETNAM | ALIBABA CLOUD | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[5\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 53.104.245.173 | TCP | 89 | 5057002 | CHINA | DIGITALOCEAN LLC | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[6\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 27.60.107.143 | TCP | 139 | 9433107 | NORTH KOREA | BULLETPROOF HOSTING SRL | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[7\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 219.84.166.226 | TCP | 42 | 2830412 | SINGAPORE | BULLETPROOF HOSTING SRL | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[8\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 211.134.237.199 | TCP | 328 | 3117050 | BRAZIL | GOOGLE LLC | Minnehaha | cf01ec94-ef3d-475c-a53d-f96ae7f8b486:evidence\[9\] \(source 7\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 123.88.74.248 | TCP | 115 | 5159465 | NIGERIA | HETZNER ONLINE GMBH | Minnehaha | 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[1\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 47.123.154.67 | TCP | 297 | 4964514 | UNITED KINGDOM | AMAZON.COM INC | Minnehaha | 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[3\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 220.119.185.35 | TCP | 698209 | 2882415 | IRELAND | ALIBABA CLOUD | Minnehaha | 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[5\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 191.182.165.253 | TCP | 137 | 7755699 | NIGERIA | MICROSOFT CORP | Minnehaha | 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[6\] \(source 8\) |
| 2026-11-03T14:45:00+00:00 → 2026-11-03T14:59:59.999000+00:00 | 192.168.213.37 | 193.163.215.13 | TCP | 45 | 7587879 | NETHERLANDS | FASTLY INC | Minnehaha | 47b842b9-6243-4a8e-9873-422fa70a0648:evidence\[8\] \(source 8\) |

### Highlighted indicators
- 123.88.74.248: destination, related; supplied unverified labels: company=HETZNER ONLINE GMBH, country=NIGERIA
- 161.84.194.247: destination, related; supplied unverified labels: company=OVH SAS, country=BRAZIL
- 162.80.36.139: destination, related; supplied unverified labels: company=SELECTEL, country=NORTH KOREA

### Key evidence
- Detector-reported observation retained. \[bd3f989d-0569-4cd3-bda1-052d5b310943:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## HIGH: 192.168.90.116
Incident: host:192.168.90.116@2026-11-03T14:30:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fanout: 22.0 distinct external destinations; baseline mean 4.875; z-score 9.174198563499223. Finding 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4.
- egress\_volume: 10.0 distinct destinations of uploads of 100 MB or more; baseline mean 0.5; z-score 19.0. Finding 8a3c0850-66ae-4f83-be24-f32416b0d71c.
- protocol\_mix: 22.0 distinct destinations over one protocol; baseline mean 4.875; z-score 9.174198563499223. Finding 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97.
- Supplied sample: 17 unique exact rows from 30 occurrences; 1 sources; 16 destinations; sent-byte sample sum 138239184973 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 196.114.197.152 | TCP | 16690565153 | 6286988 | BRAZIL | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[0\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[0\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 75.90.166.225 | TCP | 26706192780 | 4276329 | GERMANY | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[1\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[1\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 143.151.106.68 | TCP | 20449661211 | 8956285 | JAPAN | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[2\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[2\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 105.38.253.158 | TCP | 4233084353 | 282963 | FRANCE | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[3\] \(source 3\); 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[2\] \(source 4\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[3\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 89.45.207.136 | TCP | 4048062862 | 4456300 | INDIA | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[4\] \(source 3\); 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[5\] \(source 4\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[4\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 143.65.61.82 | TCP | 7370240033 | 1872187 | SWEDEN | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[5\] \(source 3\); 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[7\] \(source 4\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[5\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 134.158.210.138 | TCP | 25731076305 | 1839744 | JAPAN | DIGITALOCEAN LLC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[6\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[6\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 117.111.229.185 | TCP | 402638 | 4009280 | FRANCE | AMAZON.COM INC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[7\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[7\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 36.110.186.31 | TCP | 772612 | 9893403 | JAPAN | FASTLY INC | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[8\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[8\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 88.116.5.17 | TCP | 328344 | 8625637 | NETHERLANDS | MICROSOFT CORP | Lake Minnetonka | 89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:evidence\[9\] \(source 3\); 3d5aa0f3-8963-4cd4-b0c6-70a84206cc97:evidence\[9\] \(source 5\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 196.114.197.152 | TCP | 2085235952 | 5338223 | BRAZIL | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[0\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 146.143.192.10 | TCP | 3613570431 | 6637460 | INDIA | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[1\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 37.187.145.65 | TCP | 4100199404 | 1280633 | JAPAN | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[3\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 39.67.106.78 | TCP | 5965793351 | 4482463 | UNITED STATES | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[4\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 70.135.4.89 | TCP | 7145980841 | 8988278 | SINGAPORE | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[6\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 76.145.78.34 | TCP | 9111990910 | 6652683 | BRAZIL | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[8\] \(source 4\) |
| 2026-11-03T14:30:00+00:00 → 2026-11-03T14:44:59.999000+00:00 | 192.168.90.116 | 80.220.166.11 | TCP | 986027793 | 6395222 | UNITED KINGDOM | DIGITALOCEAN LLC | Lake Minnetonka | 8a3c0850-66ae-4f83-be24-f32416b0d71c:evidence\[9\] \(source 4\) |

### Highlighted indicators
- 105.38.253.158: destination, related; supplied unverified labels: company=DIGITALOCEAN LLC, country=FRANCE
- 117.111.229.185: destination, related; supplied unverified labels: company=AMAZON.COM INC, country=FRANCE
- 134.158.210.138: destination, related; supplied unverified labels: company=DIGITALOCEAN LLC, country=JAPAN

### Key evidence
- Detector-reported observation retained. \[89fb5fd8-df00-47a1-bab0-e0d2d4c872b4:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## HIGH: Nicollet Island
Incident: site:Nicollet Island@2026-11-03T15:30:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- site\_volume: 38.0 distinct active hosts; baseline mean 8.0; z-score None. Finding a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd.
- Supplied sample: 10 unique exact rows from 10 occurrences; 10 sources; 9 destinations; sent-byte sample sum 2778654 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.21.177 | 36.110.186.31 | TCP | 228844 | 9767263 | JAPAN | FASTLY INC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[0\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.120.115 | 18.180.25.0 | TCP | 587146 | 9632552 | UNITED KINGDOM | DIGITALOCEAN LLC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[1\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 10.10.252.86 | 133.181.130.151 | TCP | 185870 | 9659551 | GERMANY | ALIBABA CLOUD | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[2\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.147.98 | 121.170.129.5 | TCP | 190500 | 4938319 | UNITED KINGDOM | CLOUDFLARE INC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[3\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.144.164 | 144.45.247.96 | UDP | 15406 | 6806944 | FRANCE | OVH SAS | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[4\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.154.170 | 215.159.107.22 | TCP | 473595 | 2352516 | SWEDEN | MICROSOFT CORP | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[5\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.142.132 | 190.74.234.176 | TCP | 409994 | 385701 | INDIA | HETZNER ONLINE GMBH | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[6\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.123.84 | 121.170.129.5 | UDP | 49239 | 8873394 | UNITED KINGDOM | CLOUDFLARE INC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[7\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.138.170 | 76.30.148.62 | TCP | 99800 | 1476256 | SWEDEN | GOOGLE LLC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[8\] \(source 15\) |
| 2026-11-03T15:30:00+00:00 → 2026-11-03T15:44:59.999000+00:00 | 192.168.123.241 | 176.85.112.238 | TCP | 538260 | 9174640 | UNITED STATES | CLOUDFLARE INC | Nicollet Island | a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:evidence\[9\] \(source 15\) |

### Highlighted indicators
- 10.10.252.86: source, related; supplied unverified labels: unknown
- 121.170.129.5: destination, related; supplied unverified labels: company=CLOUDFLARE INC, country=UNITED KINGDOM
- 133.181.130.151: destination, related; supplied unverified labels: company=ALIBABA CLOUD, country=GERMANY

### Key evidence
- Detector-reported observation retained. \[a2b6a948-07ad-4c6c-93d8-ff790dcdc2cd:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## MEDIUM: 192.168.194.160
Incident: host:192.168.194.160@2026-11-03T15:00:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fanout: 20.0 distinct external destinations; baseline mean 5.25; z-score 9.447561074500141. Finding 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8.
- geo\_spread: 16.0 distinct destination countries; baseline mean 4.5625; z-score 9.350863184629008. Finding 7d30421f-b18b-439d-afd9-2b1e48aea1f0.
- company\_spread: 11.0 distinct destination companies; baseline mean 4.3125; z-score 5.777456944569615. Finding bac626f0-8ba6-446b-9b96-021fb8303c88.
- protocol\_mix: 18.0 distinct destinations over one protocol; baseline mean 4.6875; z-score 8.272234538103575. Finding 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3.
- Supplied sample: 18 unique exact rows from 40 occurrences; 1 sources; 16 destinations; sent-byte sample sum 1672726 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 46.90.69.86 | TCP | 79191 | 2270664 | RUSSIA | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[0\] \(source 10\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[0\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 116.182.215.67 | TCP | 102917 | 6246801 | ROMANIA | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[1\] \(source 10\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[1\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 163.164.248.62 | TCP | 80315 | 4447377 | NIGERIA | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[2\] \(source 10\); 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[8\] \(source 11\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[9\] \(source 12\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[2\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 128.225.5.163 | TCP | 161339 | 3052787 | INDIA | SELECTEL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[3\] \(source 10\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[7\] \(source 12\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[3\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 122.245.178.208 | TCP | 37866 | 2728388 | IRELAND | LIDEN DATA INTERNETWORK AB | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[4\] \(source 10\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[1\] \(source 12\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[4\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 117.145.255.128 | TCP | 35581 | 4020921 | IRAN | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[5\] \(source 10\); 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[9\] \(source 11\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[5\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 111.44.178.92 | TCP | 84026 | 1375746 | VIETNAM | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[6\] \(source 10\); 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[2\] \(source 11\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[6\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 182.249.9.208 | TCP | 158900 | 6419620 | SINGAPORE | M247 LTD | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[7\] \(source 10\); 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[5\] \(source 11\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[7\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 112.224.130.90 | TCP | 109189 | 7425623 | CHINA | BULLETPROOF HOSTING SRL | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[8\] \(source 10\); 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[3\] \(source 11\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[8\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 176.181.205.84 | TCP | 19462 | 5627599 | JAPAN | ENGIE SA | Mississippi | 8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:evidence\[9\] \(source 10\); 0d23c51d-e9b4-43f8-b0ed-a101bf69dab3:evidence\[9\] \(source 13\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 15.1.223.239 | TCP | 192573 | 1360001 | SWEDEN | M247 LTD | Mississippi | 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[0\] \(source 11\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[0\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 220.119.185.35 | UDP | 42949 | 9387888 | IRELAND | ALIBABA CLOUD | Mississippi | 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[1\] \(source 11\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[8\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 76.184.109.160 | TCP | 62184 | 1994232 | NORTH KOREA | BULLETPROOF HOSTING SRL | Mississippi | 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[4\] \(source 11\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 174.154.98.150 | TCP | 200825 | 7030581 | BRAZIL | CLOUDFLARE INC | Mississippi | 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[6\] \(source 11\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[5\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 117.111.229.185 | TCP | 105477 | 8187640 | FRANCE | AMAZON.COM INC | Mississippi | 7d30421f-b18b-439d-afd9-2b1e48aea1f0:evidence\[7\] \(source 11\); bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[4\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 182.249.9.208 | TCP | 35769 | 99542 | SINGAPORE | CHOOPA LLC | Mississippi | bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[2\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 17.107.106.4 | UDP | 26992 | 3028650 | UNITED KINGDOM | TENCENT CLOUD | Mississippi | bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[3\] \(source 12\) |
| 2026-11-03T15:00:00+00:00 → 2026-11-03T15:14:59.999000+00:00 | 192.168.194.160 | 15.1.223.239 | TCP | 137171 | 6321215 | SWEDEN | ENGIE SA | Mississippi | bac626f0-8ba6-446b-9b96-021fb8303c88:evidence\[6\] \(source 12\) |

### Highlighted indicators
- 111.44.178.92: destination, related; supplied unverified labels: company=BULLETPROOF HOSTING SRL, country=VIETNAM
- 112.224.130.90: destination, related; supplied unverified labels: company=BULLETPROOF HOSTING SRL, country=CHINA
- 116.182.215.67: destination, related; supplied unverified labels: company=BULLETPROOF HOSTING SRL, country=ROMANIA

### Key evidence
- Detector-reported observation retained. \[8fe376bd-9ef9-4efd-98b8-0c0b7fb482b8:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "conflicting\_enrichment", "indicator": "182.249.9.208"\}
- \{"kind": "conflicting\_enrichment", "indicator": "15.1.223.239"\}
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}

## LOW: 10.10.74.206
Incident: host:10.10.74.206@2026-11-03T10:30:00+00:00; disposition: needs_review; analysis: completed; synthetic: True.

TEST STUB: synthetic fixture findings require analyst review; no live narrative generated.

### Detector facts
- fanout: 7.0 distinct external destinations; baseline mean 3.0; z-score 5.059644256269407. Finding 12bce24b-26ee-4921-984f-715b9c28fa0c.
- protocol\_mix: 7.0 distinct destinations over one protocol; baseline mean 3.0; z-score 5.059644256269407. Finding f8086c60-1774-430f-84a3-c646621d1b29.
- Supplied sample: 7 unique exact rows from 14 occurrences; 1 sources; 7 destinations; sent-byte sample sum 3183980 (not an incident total).
- No domains supplied.

### Extracted IOC fields

Candidate observations only; repeated evidence references are not independent corroboration.
Missing or null values are shown as unknown; zero bytes remain zero.

| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 88.116.5.17 | TCP | 398773 | 2988777 | NETHERLANDS | MICROSOFT CORP | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[0\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[0\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 57.54.58.60 | TCP | 786534 | 2058610 | BRAZIL | FASTLY INC | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[1\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[1\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 66.83.99.99 | TCP | 176108 | 3463953 | FRANCE | LINODE LLC | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[2\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[2\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 34.175.33.74 | TCP | 537385 | 244719 | CANADA | FASTLY INC | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[3\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[3\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 54.176.10.84 | TCP | 542204 | 5611971 | UNITED STATES | OVH SAS | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[4\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[4\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 115.25.193.218 | TCP | 144060 | 6463832 | FRANCE | AMAZON.COM INC | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[5\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[5\] \(source 2\) |
| 2026-11-03T10:30:00+00:00 → 2026-11-03T10:44:59.999000+00:00 | 10.10.74.206 | 197.235.38.224 | TCP | 598916 | 8473950 | UNITED KINGDOM | CLOUDFLARE INC | Lake Minnetonka | 12bce24b-26ee-4921-984f-715b9c28fa0c:evidence\[6\] \(source 1\); f8086c60-1774-430f-84a3-c646621d1b29:evidence\[6\] \(source 2\) |

### Highlighted indicators
- 10.10.74.206: entity, source; supplied unverified labels: unknown
- 115.25.193.218: destination, related; supplied unverified labels: company=AMAZON.COM INC, country=FRANCE
- 197.235.38.224: destination, related; supplied unverified labels: company=CLOUDFLARE INC, country=UNITED KINGDOM

### Key evidence
- Detector-reported observation retained. \[12bce24b-26ee-4921-984f-715b9c28fa0c:observed\]

### Hypotheses—not conclusions
- Hypothesis: authorized operational activity may explain the anomaly.

### Limitations
- TEST STUB. Domains were not supplied in the main fixture. Endpoint and business context absent; sample coverage and byte direction are uncertain.

### Next analyst checks
- Check asset ownership and approved jobs for the supplied window.
- Review endpoint and flow logs to verify the reported activity.

### Data-quality notes
- \{"kind": "byte\_direction\_assumed", "detail": "POC assumption: bytes\_sent and bytes\_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."\}
