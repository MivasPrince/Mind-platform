# MIND Platform Metrics Documentation

> **Comprehensive Guide to Analytics Metrics Across All Dashboards**

This document provides detailed explanations of every metric tracked in the MIND Platform Analytics Dashboard, organized by user role. Each metric includes its calculation method, business significance, interpretation guidelines, and data dependencies.

---

## Table of Contents

1. [Administrator Dashboard Metrics](#administrator-dashboard-metrics)
2. [Developer Dashboard Metrics](#developer-dashboard-metrics)
3. [Faculty Dashboard Metrics](#faculty-dashboard-metrics)
4. [Student Dashboard Metrics](#student-dashboard-metrics)
5. [Future Metrics (Not Yet Available)](#future-metrics-not-yet-available)
6. [Metric Calculation Reference](#metric-calculation-reference)

---

## Administrator Dashboard Metrics

### Overview Tab

#### 1. Total Users
**Definition:** The total count of unique user accounts registered in the platform.

**Calculation:**
```sql
SELECT COUNT(DISTINCT user_id) as total_users
FROM `mind_analytics.user`
```

**Business Significance:**
- Measures platform adoption and reach
- Key indicator for institutional engagement
- Used for capacity planning and resource allocation

**Interpretation:**
- **Growing trend:** Successful platform adoption
- **Plateau:** May indicate marketing/outreach needs
- **Decline:** Investigate user retention issues

**Data Dependencies:**
- `user` table must exist
- `user_id` must be unique and non-null

**Limitations:**
- Does not distinguish between active and inactive accounts
- Includes all roles (admin, developer, faculty, student)

---

#### 2. Active Users (Last 7 Days)
**Definition:** Count of unique users who have performed any action (login, submission, session) within the past 7 days.

**Calculation:**
```sql
SELECT COUNT(DISTINCT user_id) as active_users
FROM `mind_analytics.sessions`
WHERE start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

**Business Significance:**
- Measures actual platform usage vs. registered accounts
- Key performance indicator for engagement
- Critical for understanding user retention

**Interpretation:**
- **High percentage (>40% of total users):** Strong engagement
- **Moderate (20-40%):** Typical for educational platforms
- **Low (<20%):** Engagement concerns

**Calculation Example:**
```
If Total Users = 1000
And Active Users = 350
Then Activity Rate = 35% (healthy engagement)
```

**Data Dependencies:**
- `sessions` table with accurate timestamps
- User activity properly logged

**Limitations:**
- Definition of "active" may need refinement (e.g., distinguish between login vs. meaningful engagement)
- Does not weight activity (one login = one submission)

---

#### 3. Average Grade
**Definition:** Mean final score across all graded submissions in the system.

**Calculation:**
```sql
SELECT ROUND(AVG(final_score), 2) as avg_grade
FROM `mind_analytics.grades`
WHERE final_score IS NOT NULL
```

**Business Significance:**
- Overall learning effectiveness indicator
- Benchmark for academic standards
- Used for quality assurance and curriculum adjustment

**Interpretation:**
- **90-100%:** Excellent learning outcomes (or potentially too easy)
- **80-89%:** Good performance
- **70-79%:** Satisfactory, room for improvement
- **<70%:** May indicate curriculum/instruction issues

**Contextual Factors:**
- Compare to institutional benchmarks
- Consider case study difficulty levels
- Account for student cohort characteristics

**Data Dependencies:**
- `grades.final_score` populated and accurate
- Sufficient sample size for statistical validity

**Limitations:**
- Simple mean doesn't account for score distribution
- No weighting by case study difficulty
- Doesn't distinguish between student levels (freshman vs. senior)

---

#### 4. System Uptime
**Definition:** Percentage of time the system was operational and accessible over the past 30 days.

**Calculation:**
```sql
-- Simplified calculation based on error rate
SELECT 
  ROUND((1 - (error_count / total_requests)) * 100, 2) as uptime_percentage
FROM (
  SELECT 
    COUNT(*) as total_requests,
    COUNTIF(derived_is_error = TRUE) as error_count
  FROM `mind_analytics.backend_telemetry`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
)
```

**Business Significance:**
- Service level agreement (SLA) compliance
- User experience quality indicator
- Infrastructure reliability measure

**Industry Standards:**
- **99.9% ("three nines"):** High availability (43 minutes downtime/month)
- **99.5%:** Acceptable (3.6 hours downtime/month)
- **<99%:** Significant reliability issues

**Interpretation:**
- **>99.9%:** Excellent reliability
- **99.5-99.9%:** Good but improvable
- **<99.5%:** Urgent infrastructure attention needed

**Data Dependencies:**
- `backend_telemetry` table with comprehensive logging
- Accurate error detection and flagging

**Limitations:**
- Current implementation approximates uptime from error rates
- Doesn't account for scheduled maintenance windows
- May not capture complete system unavailability (if logging fails)

**Recommended Enhancement:**
- Implement external monitoring service (e.g., Pingdom, UptimeRobot)
- Track actual HTTP 200 vs. 5xx responses
- Separate maintenance windows from actual downtime

---

#### 5. Weekly Growth Rate
**Definition:** Percentage change in new user registrations compared to the previous week.

**Calculation:**
```sql
WITH weekly_signups AS (
  SELECT 
    DATE_TRUNC(date_added, WEEK) as week,
    COUNT(*) as signups
  FROM `mind_analytics.user`
  GROUP BY week
  ORDER BY week DESC
  LIMIT 2
)
SELECT 
  ROUND(
    ((current_week.signups - previous_week.signups) / previous_week.signups) * 100, 
    2
  ) as growth_rate
FROM 
  (SELECT signups FROM weekly_signups LIMIT 1) current_week,
  (SELECT signups FROM weekly_signups LIMIT 1 OFFSET 1) previous_week
```

**Business Significance:**
- Measures platform adoption momentum
- Indicates marketing/outreach effectiveness
- Early warning for declining interest

**Interpretation:**
- **Positive growth:** Platform gaining traction
- **Zero growth:** Steady state (may be mature platform)
- **Negative growth:** Investigate causes (competition, quality issues, end of enrollment period)

**Seasonal Considerations:**
- Academic calendar affects enrollments
- Compare year-over-year, not just week-over-week
- Account for marketing campaigns and institutional events

**Data Dependencies:**
- `user.date_added` accurately records registration timestamp
- Sufficient historical data (at least 2 weeks)

---

### User Analytics Tab

#### 6. Users by Department
**Definition:** Distribution of registered users across academic departments.

**Calculation:**
```sql
SELECT 
  department,
  COUNT(*) as user_count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM `mind_analytics.user`
WHERE department IS NOT NULL
GROUP BY department
ORDER BY user_count DESC
```

**Business Significance:**
- Resource allocation by department
- Platform adoption by academic unit
- Identifies high-engagement and low-engagement departments

**Visualization:** Horizontal bar chart with percentage labels

**Actionable Insights:**
- **High concentration (>50% in one department):** May need targeted outreach to other departments
- **Balanced distribution:** Good cross-institutional adoption
- **Missing departments:** Outreach opportunities

**Data Dependencies:**
- `user.department` field populated
- Standardized department naming conventions

**Limitations:**
- Doesn't account for department sizes (large vs. small departments)
- No weighting by user activity level

---

#### 7. Users by Role
**Definition:** Count of users in each system role (admin, developer, faculty, student).

**Calculation:**
```sql
SELECT 
  role,
  COUNT(*) as count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM `mind_analytics.user`
WHERE role IS NOT NULL
GROUP BY role
ORDER BY count DESC
```

**Business Significance:**
- Validates role distribution expectations
- Ensures appropriate access control
- Monitors admin/faculty ratios

**Expected Ratios (Typical Institution):**
- Students: 80-90%
- Faculty: 8-15%
- Admins: 1-3%
- Developers: 1-2%

**Red Flags:**
- **Too many admins (>5%):** Security concern
- **Too few faculty:** Adoption issues
- **No students:** Platform not reaching target audience

**Data Dependencies:**
- `user.role` accurately assigned
- Roles follow consistent naming (admin vs. administrator)

---

#### 8. Average Performance by Department
**Definition:** Mean final score for all graded submissions, grouped by student department.

**Calculation:**
```sql
SELECT 
  u.department,
  COUNT(DISTINCT g.user) as student_count,
  COUNT(g._id) as total_submissions,
  ROUND(AVG(g.final_score), 2) as avg_score,
  ROUND(MIN(g.final_score), 2) as min_score,
  ROUND(MAX(g.final_score), 2) as max_score
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.department
ORDER BY avg_score DESC
```

**Business Significance:**
- Identifies high-performing and struggling departments
- Informs resource allocation and support needs
- Validates program quality across institution

**Interpretation:**
- **>10 point spread between departments:** Investigate causes
  - Curriculum differences
  - Faculty quality variations
  - Student preparation levels
  - Case study relevance to discipline

**Actionable Insights:**
- High performers: Share best practices
- Low performers: Provide targeted support
- Large variances: Standardize or adjust expectations

**Statistical Considerations:**
- Minimum sample size: 30 students per department for validity
- Account for case study difficulty differences
- Consider student level (freshman vs. graduate)

---

#### 9. Average Performance by Role
**Definition:** Mean final score segmented by user role.

**Calculation:**
```sql
SELECT 
  u.role,
  COUNT(DISTINCT g.user) as user_count,
  ROUND(AVG(g.final_score), 2) as avg_score
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.role
ORDER BY avg_score DESC
```

**Business Significance:**
- Validates role definitions and access appropriateness
- Identifies if non-students are taking assessments
- Quality control check

**Expected Behavior:**
- Students should be primary grade receivers
- Faculty/admin testing should be flagged or filtered

**Data Quality Indicator:**
- If admins/developers have many grades → configuration issue
- Only students should have substantial grade records

---

#### 10. Daily Active Users (Last 30 Days)
**Definition:** Count of unique users active each day over the past month.

**Calculation:**
```sql
SELECT 
  DATE(start_time) as date,
  COUNT(DISTINCT user_id) as active_users
FROM `mind_analytics.sessions`
WHERE start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date
```

**Business Significance:**
- Usage pattern identification
- Capacity planning
- Identifies peak usage times

**Pattern Analysis:**
- **Weekday spikes:** Normal academic pattern
- **Weekend usage:** Indicate flexible learning
- **Sudden drops:** Investigate system issues or events

**Visualization:** Line chart with trend line

**Actionable Insights:**
- **High variability:** Consider load balancing strategies
- **Declining trend:** Engagement intervention needed
- **Consistent growth:** Successful adoption

---

### Learning Metrics Tab

#### 11. Score Distribution
**Definition:** Frequency distribution of final scores across all graded submissions.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN final_score >= 90 THEN 'A (90-100)'
    WHEN final_score >= 80 THEN 'B (80-89)'
    WHEN final_score >= 70 THEN 'C (70-79)'
    WHEN final_score >= 60 THEN 'D (60-69)'
    ELSE 'F (<60)'
  END as grade_range,
  COUNT(*) as count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM `mind_analytics.grades`
WHERE final_score IS NOT NULL
GROUP BY grade_range
ORDER BY grade_range
```

**Business Significance:**
- Academic rigor validation
- Grade inflation/deflation detection
- Learning outcome assessment

**Ideal Distribution (Normal Curve):**
- A (90-100): 15-25%
- B (80-89): 30-40%
- C (70-79): 25-35%
- D (60-69): 5-15%
- F (<60): 5-10%

**Red Flags:**
- **>50% As:** Possible grade inflation or too-easy content
- **>30% Fs:** Content too difficult or instruction issues
- **Bimodal distribution:** Mixed student preparation levels

**Visualization:** Bar chart with target range overlay

---

#### 12. At-Risk Student Count
**Definition:** Number of students with average scores below a defined threshold (default: 70%).

**Calculation:**
```sql
SELECT COUNT(*) as at_risk_count
FROM (
  SELECT 
    user,
    AVG(final_score) as avg_score
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
  HAVING AVG(final_score) < 70
)
```

**Business Significance:**
- Early intervention identification
- Resource allocation for student support
- Retention and success metric

**Intervention Thresholds:**
- **Critical (<60%):** Immediate intervention required
- **At-Risk (60-70%):** Proactive support recommended
- **Borderline (70-75%):** Monitor closely

**Actionable Insights:**
- Generate intervention lists for academic advisors
- Trigger automated outreach emails
- Allocate tutoring resources

**Calculation Variants:**
- Adjust threshold based on institutional standards
- Consider trajectory (declining vs. stable low performers)
- Account for number of attempts (struggling vs. new)

---

#### 13. Submissions Over Time
**Definition:** Daily count of graded case study submissions.

**Calculation:**
```sql
SELECT 
  DATE(timestamp) as date,
  COUNT(_id) as submissions
FROM `mind_analytics.grades`
WHERE timestamp IS NOT NULL
GROUP BY date
ORDER BY date
```

**Business Significance:**
- Workload distribution visibility
- Deadline identification
- System capacity planning

**Pattern Analysis:**
- **Spikes:** Assignment deadlines
- **Valleys:** Breaks or low-activity periods
- **Gradual increase:** Growing engagement

**Operational Use:**
- **High-volume days:** Scale infrastructure
- **Low-activity predictions:** Schedule maintenance
- **Trend analysis:** Forecast future load

**Data Quality Check:**
- Sudden zero submissions = logging issue
- Implausible volumes = data duplication

---

#### 14. Weekly Activity Volume
**Definition:** Count of graded submissions aggregated by calendar week.

**Calculation:**
```sql
SELECT 
  DATE_TRUNC(timestamp, WEEK) as week,
  COUNT(_id) as submissions,
  COUNT(DISTINCT user) as unique_students
FROM `mind_analytics.grades`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 WEEK)
GROUP BY week
ORDER BY week
```

**Business Significance:**
- Semester-level activity tracking
- Identifies busy and slow periods
- Academic calendar alignment validation

**Seasonal Patterns:**
- **Weeks 1-4 (Semester start):** Low activity (orientation)
- **Weeks 5-10 (Mid-semester):** Peak activity
- **Weeks 11-13 (Finals):** Spike then drop
- **Breaks:** Near-zero activity

**Comparative Analysis:**
- Year-over-year comparison
- Semester-over-semester trends
- Impact of policy changes

---

### AI Resources Tab

#### 15. Total AI Tokens Used
**Definition:** Cumulative count of all tokens consumed by AI models across all interactions.

**Calculation:**
```sql
SELECT 
  SUM(derived_ai_total_tokens) as total_tokens,
  ROUND(SUM(derived_ai_total_tokens) / 1000000.0, 2) as millions_of_tokens
FROM `mind_analytics.backend_telemetry`
WHERE derived_ai_total_tokens IS NOT NULL
  AND derived_ai_model IS NOT NULL
```

**Business Significance:**
- Primary AI cost driver
- Resource consumption tracking
- Budget forecasting

**Token Consumption Context:**
- **Input tokens:** User prompts and context
- **Output tokens:** AI-generated responses
- **Typical ratio:** 1:2 (input:output)

**Cost Calculation:**
```
Estimated Cost = (Total Tokens / 1,000,000) × $15
Example: 10M tokens = $150
```

**Budgeting Considerations:**
- Track monthly trends
- Set alerts for unusual spikes
- Compare to per-user average

---

#### 16. AI Models Used
**Definition:** Count of requests served by each AI model type.

**Calculation:**
```sql
SELECT 
  derived_ai_model as model,
  COUNT(*) as request_count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage,
  SUM(derived_ai_total_tokens) as total_tokens
FROM `mind_analytics.backend_telemetry`
WHERE derived_ai_model IS NOT NULL
GROUP BY model
ORDER BY request_count DESC
```

**Business Significance:**
- Model usage optimization
- Cost allocation by model
- Performance vs. cost trade-offs

**Model Characteristics:**
- **GPT-4:** High accuracy, high cost
- **GPT-3.5:** Balanced performance, moderate cost
- **Claude:** Alternative pricing, different strengths

**Optimization Opportunities:**
- Route simple queries to cheaper models
- Use expensive models only for complex tasks
- A/B test model quality vs. cost

---

#### 17. Tokens by Model Over Time
**Definition:** Daily token consumption segmented by AI model.

**Calculation:**
```sql
SELECT 
  DATE(created_at) as date,
  derived_ai_model as model,
  SUM(derived_ai_total_tokens) as tokens
FROM `mind_analytics.backend_telemetry`
WHERE derived_ai_model IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date, model
ORDER BY date, model
```

**Business Significance:**
- Cost trend analysis
- Model performance comparison over time
- Identifies optimization opportunities

**Visualization:** Stacked area chart showing contribution by model

**Analysis Questions:**
- Is expensive model usage increasing?
- Can we shift workload to cheaper models?
- Are usage spikes justified by value?

---

#### 18. Estimated AI Costs
**Definition:** Projected monthly expenditure based on current token usage and standard pricing.

**Calculation:**
```sql
WITH daily_tokens AS (
  SELECT 
    DATE(created_at) as date,
    SUM(derived_ai_total_tokens) as tokens
  FROM `mind_analytics.backend_telemetry`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND derived_ai_model IS NOT NULL
  GROUP BY date
)
SELECT 
  ROUND(AVG(tokens), 0) as avg_daily_tokens,
  ROUND(AVG(tokens) * 30, 0) as projected_monthly_tokens,
  ROUND((AVG(tokens) * 30 / 1000000.0) * 15, 2) as estimated_monthly_cost
FROM daily_tokens
```

**Pricing Assumptions:**
- $15 per 1M tokens (blended rate)
- Actual pricing varies by model and provider

**Budgeting Use Cases:**
- Monthly expense forecasting
- Cost per student calculation
- ROI analysis

**Cost Optimization Strategies:**
- Implement caching for repeated queries
- Use prompt engineering to reduce tokens
- Route to cheaper models when appropriate

---

### System Health Tab

#### 19. Total Requests (30 Days)
**Definition:** Count of all HTTP requests to the backend API over the past 30 days.

**Calculation:**
```sql
SELECT COUNT(*) as total_requests
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
```

**Business Significance:**
- System utilization metric
- Capacity planning baseline
- Scaling decisions

**Typical Patterns:**
- **Per-user average:** 10-50 requests/day
- **Spikes:** 2-3x normal during peak hours
- **Growth rate:** Should correlate with user growth

---

#### 20. Success Rate
**Definition:** Percentage of requests that completed successfully (non-error responses).

**Calculation:**
```sql
SELECT 
  ROUND(
    (COUNTIF(derived_is_error = FALSE) * 100.0 / COUNT(*)),
    2
  ) as success_rate
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
```

**Business Significance:**
- Service reliability indicator
- User experience quality
- SLA compliance metric

**Target Thresholds:**
- **>99.5%:** Excellent
- **98-99.5%:** Good
- **<98%:** Needs attention

**Error Analysis:**
- Identify most common error types
- Investigate patterns (time-based, route-based)
- Prioritize fixes by impact

---

#### 21. Average Response Time
**Definition:** Mean time between request initiation and response completion.

**Calculation:**
```sql
SELECT 
  ROUND(AVG(derived_response_time_ms), 2) as avg_response_ms,
  ROUND(AVG(derived_response_time_ms) / 1000.0, 3) as avg_response_seconds
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND derived_response_time_ms IS NOT NULL
```

**Business Significance:**
- User experience quality
- System performance indicator
- Infrastructure capacity assessment

**Performance Standards:**
- **<500ms:** Excellent (feels instant)
- **500-1000ms:** Good (acceptable)
- **1000-2000ms:** Moderate (noticeable delay)
- **>2000ms:** Poor (frustrating for users)

**Factors Affecting Response Time:**
- Database query complexity
- AI model processing time
- Network latency
- Server load

---

#### 22. P95 Response Time
**Definition:** 95th percentile response time - the threshold below which 95% of requests complete.

**Calculation:**
```sql
SELECT 
  ROUND(
    PERCENTILE_CONT(derived_response_time_ms, 0.95) OVER (),
    2
  ) as p95_response_ms
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND derived_response_time_ms IS NOT NULL
LIMIT 1
```

**Business Significance:**
- Captures tail latency (worst-case scenarios)
- More representative than average for user experience
- SLA metric for premium services

**Why P95 Matters:**
- Average can hide problems (a few slow requests)
- P95 shows what most users actually experience
- Helps identify outliers and performance issues

**Target P95:**
- **<1000ms:** Excellent
- **1000-2000ms:** Good
- **>2000ms:** Investigation needed

---

#### 23. Error Rate Over Time
**Definition:** Percentage of failed requests per hour over the past 24 hours.

**Calculation:**
```sql
SELECT 
  TIMESTAMP_TRUNC(created_at, HOUR) as hour,
  COUNT(*) as total_requests,
  COUNTIF(derived_is_error = TRUE) as error_count,
  ROUND((COUNTIF(derived_is_error = TRUE) * 100.0 / COUNT(*)), 2) as error_rate
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour
```

**Business Significance:**
- Incident detection
- Service health monitoring
- Identifies error patterns

**Alert Thresholds:**
- **>5% error rate:** Immediate investigation
- **2-5%:** Monitor closely
- **<2%:** Normal operation

**Pattern Recognition:**
- **Sudden spike:** System incident
- **Gradual increase:** Degrading service
- **Periodic errors:** Scheduled job failures

---

#### 24. Route Performance
**Definition:** Average response time grouped by API endpoint.

**Calculation:**
```sql
SELECT 
  http_route as route,
  COUNT(*) as request_count,
  ROUND(AVG(derived_response_time_ms), 2) as avg_response_ms,
  ROUND(MAX(derived_response_time_ms), 2) as max_response_ms,
  COUNTIF(derived_is_error = TRUE) as error_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND http_route IS NOT NULL
GROUP BY route
ORDER BY avg_response_ms DESC
```

**Business Significance:**
- Identifies slow endpoints
- Optimization prioritization
- Load distribution analysis

**Optimization Strategy:**
- Focus on high-traffic, slow routes
- Implement caching for heavy routes
- Optimize database queries for slow endpoints

**Red Flags:**
- Routes >3000ms average → immediate optimization needed
- High error count on critical routes → stability issue

---

## Developer Dashboard Metrics

### Overview Tab

#### 25. API Requests (Today)
**Definition:** Total count of API requests received since midnight (server time).

**Calculation:**
```sql
SELECT COUNT(*) as requests_today
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
```

**Business Significance:**
- Daily load monitoring
- Capacity planning
- Anomaly detection

**Usage:**
- Compare to historical average
- Identify unusual spikes or drops
- Trigger scaling decisions

---

#### 26. Success Rate (Today)
**Definition:** Percentage of non-error responses for today's requests.

**Calculation:**
```sql
SELECT 
  ROUND((COUNTIF(derived_is_error = FALSE) * 100.0 / COUNT(*)), 2) as success_rate
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
```

**Business Significance:**
- Real-time service health
- Incident detection
- SLA monitoring

**Alert Triggers:**
- <99% → Warning
- <98% → Critical

---

#### 27. Average Latency (Today)
**Definition:** Mean response time for all requests today.

**Calculation:**
```sql
SELECT ROUND(AVG(derived_response_time_ms), 2) as avg_latency_ms
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
  AND derived_response_time_ms IS NOT NULL
```

**Business Significance:**
- Performance baseline
- Degradation detection
- User experience indicator

---

#### 28. P95 Latency (Today)
**Definition:** 95th percentile response time for today.

**Calculation:**
```sql
SELECT 
  ROUND(PERCENTILE_CONT(derived_response_time_ms, 0.95) OVER (), 2) as p95_latency_ms
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
  AND derived_response_time_ms IS NOT NULL
LIMIT 1
```

**SLA Target:** <2000ms

**Business Significance:**
- Tail latency monitoring
- Premium user experience metric
- Infrastructure adequacy

---

#### 29. P99 Latency (Today)
**Definition:** 99th percentile response time - worst 1% of requests.

**Calculation:**
```sql
SELECT 
  ROUND(PERCENTILE_CONT(derived_response_time_ms, 0.99) OVER (), 2) as p99_latency_ms
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
  AND derived_response_time_ms IS NOT NULL
LIMIT 1
```

**Business Significance:**
- Extreme outlier detection
- Infrastructure bottleneck identification
- Database query optimization needs

**Interpretation:**
- P99 >> P95 → Investigate specific slow queries
- P99 ≈ P95 → Generally consistent performance

---

#### 30. Total Tokens (Today)
**Definition:** Sum of all AI tokens consumed today.

**Calculation:**
```sql
SELECT SUM(derived_ai_total_tokens) as tokens_today
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
  AND derived_ai_total_tokens IS NOT NULL
```

**Business Significance:**
- Daily cost estimation
- Usage anomaly detection
- Budget tracking

---

#### 31. Active Models (Today)
**Definition:** Count of distinct AI models invoked today.

**Calculation:**
```sql
SELECT COUNT(DISTINCT derived_ai_model) as active_models
FROM `mind_analytics.backend_telemetry`
WHERE DATE(created_at) = CURRENT_DATE()
  AND derived_ai_model IS NOT NULL
```

**Business Significance:**
- Model utilization tracking
- Failover validation
- Cost allocation

---

#### 32. Requests per Hour (Last 24h)
**Definition:** Hourly request volume for the past 24 hours.

**Calculation:**
```sql
SELECT 
  TIMESTAMP_TRUNC(created_at, HOUR) as hour,
  COUNT(*) as request_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour
```

**Visualization:** Line chart

**Business Significance:**
- Traffic pattern identification
- Peak load preparation
- Capacity planning

**Pattern Analysis:**
- **Business hours spike:** Expected academic usage
- **Night traffic:** International users or batch jobs
- **Consistent 24/7:** Bot traffic or automated processes

---

#### 33. Response Time Distribution
**Definition:** Histogram showing frequency of requests by response time buckets.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN derived_response_time_ms < 100 THEN '<100ms'
    WHEN derived_response_time_ms < 500 THEN '100-500ms'
    WHEN derived_response_time_ms < 1000 THEN '500ms-1s'
    WHEN derived_response_time_ms < 2000 THEN '1-2s'
    ELSE '>2s'
  END as response_bucket,
  COUNT(*) as request_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND derived_response_time_ms IS NOT NULL
GROUP BY response_bucket
ORDER BY response_bucket
```

**Business Significance:**
- Performance profile visualization
- Optimization target identification
- User experience assessment

**Ideal Distribution:**
- >80% under 500ms
- <5% over 2s

---

### AI Performance Tab

#### 34. Tokens by Model (Last 7 Days)
**Definition:** Token consumption aggregated by AI model over the past week.

**Calculation:**
```sql
SELECT 
  derived_ai_model as model,
  SUM(derived_ai_total_tokens) as total_tokens,
  ROUND(AVG(derived_ai_total_tokens), 0) as avg_tokens_per_request,
  COUNT(*) as request_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND derived_ai_model IS NOT NULL
GROUP BY model
ORDER BY total_tokens DESC
```

**Business Significance:**
- Cost attribution by model
- Model efficiency comparison
- Usage pattern analysis

**Efficiency Metrics:**
- **Tokens per request:** Lower is more efficient
- **Total tokens:** Primary cost driver

---

#### 35. AI Request Success Rate
**Definition:** Percentage of AI-related requests that completed without errors.

**Calculation:**
```sql
SELECT 
  ROUND(
    (COUNTIF(derived_is_error = FALSE) * 100.0 / COUNT(*)),
    2
  ) as ai_success_rate
FROM `mind_analytics.backend_telemetry`
WHERE derived_ai_model IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

**Business Significance:**
- AI service reliability
- Model availability monitoring
- Fallback strategy validation

**Target:** >99%

---

#### 36. Average Tokens per Request
**Definition:** Mean token consumption per AI invocation.

**Calculation:**
```sql
SELECT 
  ROUND(AVG(derived_ai_total_tokens), 0) as avg_tokens,
  ROUND(MIN(derived_ai_total_tokens), 0) as min_tokens,
  ROUND(MAX(derived_ai_total_tokens), 0) as max_tokens
FROM `mind_analytics.backend_telemetry`
WHERE derived_ai_model IS NOT NULL
  AND derived_ai_total_tokens IS NOT NULL
  AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

**Business Significance:**
- Cost efficiency metric
- Prompt optimization indicator
- Usage pattern validation

**Benchmarks:**
- Simple queries: 100-500 tokens
- Complex conversations: 1000-3000 tokens
- Outliers: >5000 tokens (investigate)

---

### API Analytics Tab

#### 37. Requests by HTTP Status Code
**Definition:** Count of requests grouped by HTTP response code.

**Calculation:**
```sql
SELECT 
  http_status_code as status_code,
  COUNT(*) as count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND http_status_code IS NOT NULL
GROUP BY status_code
ORDER BY count DESC
```

**Status Code Categories:**
- **2xx (Success):** Expected majority (>95%)
- **4xx (Client errors):** User/app issues (5-10% typical)
- **5xx (Server errors):** System issues (<1% target)

**Common Codes:**
- **200 (OK):** Successful request
- **400 (Bad Request):** Invalid input
- **401 (Unauthorized):** Authentication failure
- **404 (Not Found):** Invalid endpoint
- **500 (Internal Server Error):** Server crash
- **503 (Service Unavailable):** Overload or maintenance

---

#### 38. Slowest Routes
**Definition:** API endpoints ranked by average response time.

**Calculation:**
```sql
SELECT 
  http_route,
  COUNT(*) as request_count,
  ROUND(AVG(derived_response_time_ms), 2) as avg_ms,
  ROUND(MAX(derived_response_time_ms), 2) as max_ms,
  ROUND(PERCENTILE_CONT(derived_response_time_ms, 0.95) OVER (PARTITION BY http_route), 2) as p95_ms
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND http_route IS NOT NULL
  AND derived_response_time_ms IS NOT NULL
GROUP BY http_route
ORDER BY avg_ms DESC
LIMIT 10
```

**Business Significance:**
- Optimization prioritization
- Performance bottleneck identification
- API design validation

**Action Items:**
- Routes >2000ms avg → Critical optimization
- Routes >1000ms with high volume → High-priority optimization
- Database query analysis for slow routes

---

#### 39. Error Rate by Route
**Definition:** Percentage of failed requests per API endpoint.

**Calculation:**
```sql
SELECT 
  http_route,
  COUNT(*) as total_requests,
  COUNTIF(derived_is_error = TRUE) as error_count,
  ROUND((COUNTIF(derived_is_error = TRUE) * 100.0 / COUNT(*)), 2) as error_rate
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND http_route IS NOT NULL
GROUP BY http_route
HAVING error_count > 0
ORDER BY error_rate DESC
```

**Business Significance:**
- Identifies unreliable endpoints
- Guides bug fix prioritization
- API quality monitoring

**Red Flags:**
- Any route >10% error rate
- High-traffic routes >2% error rate

---

### Trace Debugger Tab

#### 40. Recent Traces
**Definition:** Individual request lifecycle details for debugging.

**Calculation:**
```sql
SELECT 
  trace_id,
  http_route,
  http_status_code,
  derived_response_time_ms,
  derived_ai_model,
  derived_ai_total_tokens,
  derived_is_error,
  created_at
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY created_at DESC
LIMIT 100
```

**Business Significance:**
- Real-time debugging
- Issue investigation
- Pattern recognition

**Use Cases:**
- Trace specific user issues
- Investigate error spikes
- Performance profiling

---

### Telemetry Tab

#### 41. Services Monitored
**Definition:** Count of distinct backend services reporting telemetry.

**Calculation:**
```sql
SELECT 
  service_name,
  COUNT(*) as request_count,
  COUNTIF(derived_is_error = TRUE) as error_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND service_name IS NOT NULL
GROUP BY service_name
ORDER BY request_count DESC
```

**Business Significance:**
- Microservice health overview
- Load distribution
- Architecture visibility

---

#### 42. Telemetry Data Volume
**Definition:** Count of telemetry records ingested per hour.

**Calculation:**
```sql
SELECT 
  TIMESTAMP_TRUNC(created_at, HOUR) as hour,
  COUNT(*) as record_count
FROM `mind_analytics.backend_telemetry`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour
```

**Business Significance:**
- Monitoring system health
- Data pipeline validation
- Storage cost estimation

---

## Faculty Dashboard Metrics

### Overview Tab

#### 43. Total Students
**Definition:** Count of unique users with student role and at least one grade record.

**Calculation:**
```sql
SELECT COUNT(DISTINCT g.user) as total_students
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE u.role = 'student'
  AND g.final_score IS NOT NULL
```

**Business Significance:**
- Class size for this instructor/department
- Resource planning
- Engagement baseline

**Faculty Context:**
- Compare to enrolled students (identify non-participants)
- Track over time (attrition vs. growth)

---

#### 44. Class Average Score
**Definition:** Mean final score across all students in the class.

**Calculation:**
```sql
SELECT ROUND(AVG(final_score), 2) as class_average
FROM `mind_analytics.grades`
WHERE final_score IS NOT NULL
```

**Business Significance:**
- Overall teaching effectiveness
- Content difficulty assessment
- Benchmark for individual student comparison

**Interpretation:**
- **>85%:** Excellent learning outcomes
- **75-85%:** Good performance
- **<75%:** Review curriculum/instruction

---

#### 45. Completion Rate
**Definition:** Percentage of enrolled students who have submitted at least one graded assignment.

**Calculation:**
```sql
WITH enrolled AS (
  SELECT COUNT(*) as total
  FROM `mind_analytics.user`
  WHERE role = 'student'
),
active AS (
  SELECT COUNT(DISTINCT user) as completed
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
)
SELECT ROUND((active.completed * 100.0 / enrolled.total), 2) as completion_rate
FROM enrolled, active
```

**Business Significance:**
- Student engagement metric
- Course accessibility indicator
- Attrition early warning

**Interpretation:**
- **>90%:** Excellent engagement
- **70-90%:** Typical
- **<70%:** Investigate barriers

---

#### 46. Average Submissions per Student
**Definition:** Mean number of graded case study submissions per student.

**Calculation:**
```sql
SELECT ROUND(AVG(submission_count), 2) as avg_submissions
FROM (
  SELECT user, COUNT(_id) as submission_count
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
)
```

**Business Significance:**
- Student engagement depth
- Course workload validation
- Persistence indicator

**Interpretation:**
- **>10 submissions:** High engagement
- **5-10 submissions:** Moderate engagement
- **<5 submissions:** Low engagement or new students

---

#### 47. At-Risk Students (Threshold-based)
**Definition:** Count of students with average scores below a configurable threshold (default 70%).

**Calculation:**
```sql
SELECT 
  u.name,
  u.department,
  COUNT(g._id) as total_submissions,
  ROUND(AVG(g.final_score), 2) as average_score,
  ROUND(MIN(g.final_score), 2) as lowest_score
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.user_id, u.name, u.department
HAVING AVG(g.final_score) < 70
ORDER BY average_score
```

**Business Significance:**
- Early intervention identification
- Academic support prioritization
- Retention initiative targeting

**Action Thresholds:**
- **<60%:** Critical - immediate intervention
- **60-70%:** At-risk - proactive support
- **70-75%:** Monitor - check-in recommended

---

#### 48. Top Performers
**Definition:** Students with highest average scores (typically top 10).

**Calculation:**
```sql
SELECT 
  u.name,
  u.department,
  COUNT(g._id) as submissions,
  ROUND(AVG(g.final_score), 2) as average_score
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.user_id, u.name, u.department
HAVING COUNT(g._id) >= 3  -- Minimum 3 submissions for validity
ORDER BY average_score DESC
LIMIT 10
```

**Business Significance:**
- Recognition and awards
- Peer mentoring candidates
- Success pattern identification

**Validation:**
- Minimum submission threshold prevents outliers
- Consider percentile rank for fairness

---

### Student Performance Tab

#### 49. Grade Distribution
**Definition:** Count of students in each letter grade category.

**Calculation:**
```sql
WITH student_averages AS (
  SELECT 
    user,
    AVG(final_score) as avg_score
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
)
SELECT 
  CASE 
    WHEN avg_score >= 90 THEN 'A'
    WHEN avg_score >= 80 THEN 'B'
    WHEN avg_score >= 70 THEN 'C'
    WHEN avg_score >= 60 THEN 'D'
    ELSE 'F'
  END as grade,
  COUNT(*) as student_count,
  ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM student_averages
GROUP BY grade
ORDER BY grade
```

**Business Significance:**
- Class performance profile
- Grading fairness validation
- Curriculum difficulty assessment

---

#### 50. Performance by Department
**Definition:** Average score grouped by student department.

**Calculation:**
```sql
SELECT 
  u.department,
  COUNT(DISTINCT g.user) as student_count,
  ROUND(AVG(g.final_score), 2) as avg_score,
  ROUND(MIN(g.final_score), 2) as min_score,
  ROUND(MAX(g.final_score), 2) as max_score
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.department
ORDER BY avg_score DESC
```

**Business Significance:**
- Cross-department comparison
- Resource allocation guidance
- Program quality assessment

---

### Case Study Analytics Tab

#### 51. Case Study Completion Counts
**Definition:** Number of graded submissions per case study.

**Calculation:**
```sql
SELECT 
  c.title as case_study,
  COUNT(g._id) as completions,
  COUNT(DISTINCT g.user) as unique_students
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.final_score IS NOT NULL
GROUP BY c.case_study_id, c.title
ORDER BY completions DESC
```

**Business Significance:**
- Case study popularity
- Workload distribution
- Engagement indicator

**Interpretation:**
- High completion → Popular or required
- Low completion → Optional, difficult, or unappealing

---

#### 52. Average Score by Case Study
**Definition:** Mean performance across all students for each case study.

**Calculation:**
```sql
SELECT 
  c.title as case_study,
  COUNT(g._id) as submissions,
  ROUND(AVG(g.final_score), 2) as avg_score,
  ROUND(MIN(g.final_score), 2) as min_score,
  ROUND(MAX(g.final_score), 2) as max_score,
  ROUND(STDDEV(g.final_score), 2) as std_dev
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.final_score IS NOT NULL
GROUP BY c.case_study_id, c.title
ORDER BY avg_score
```

**Business Significance:**
- Case study difficulty assessment
- Content quality validation
- Curriculum balance

**Interpretation:**
- **Low avg + high std_dev:** Difficult, polarizing
- **High avg + low std_dev:** Well-designed, appropriate difficulty
- **Low avg + low std_dev:** Too difficult for cohort

---

#### 53. Case Study Engagement Rate
**Definition:** Percentage of students who attempted each case study.

**Calculation:**
```sql
WITH total_students AS (
  SELECT COUNT(DISTINCT user) as total
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
)
SELECT 
  c.title,
  COUNT(DISTINCT g.user) as students_attempted,
  ROUND((COUNT(DISTINCT g.user) * 100.0 / ts.total), 2) as engagement_rate
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
CROSS JOIN total_students ts
WHERE g.final_score IS NOT NULL
GROUP BY c.case_study_id, c.title, ts.total
ORDER BY engagement_rate DESC
```

**Business Significance:**
- Case study appeal
- Curriculum design validation
- Student preference insights

---

### At-Risk Students Tab

#### 54. Students Below Threshold
**Definition:** List of students with customizable score threshold (slider-controlled).

**Calculation:**
```sql
-- Threshold set by user via slider (default 70%)
SELECT 
  u.name,
  u.department,
  COUNT(g._id) as total_submissions,
  ROUND(AVG(g.final_score), 2) as average_score,
  ROUND(MIN(g.final_score), 2) as lowest_score,
  MAX(g.timestamp) as last_activity
FROM `mind_analytics.grades` g
JOIN `mind_analytics.user` u ON g.user = u.user_id
WHERE g.final_score IS NOT NULL
GROUP BY u.user_id, u.name, u.department
HAVING AVG(g.final_score) < [threshold_value]
ORDER BY average_score
```

**Business Significance:**
- Intervention list generation
- Academic support prioritization
- Retention initiative targeting

**Recommended Actions by Score:**
- **<50%:** Immediate counseling, consider withdrawal
- **50-60%:** Intensive tutoring, study skills workshop
- **60-70%:** Regular check-ins, supplemental resources

---

#### 55. Inactive Students
**Definition:** Students who haven't submitted in 7+ days.

**Calculation:**
```sql
WITH last_activity AS (
  SELECT 
    user,
    MAX(timestamp) as last_submission
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
)
SELECT 
  u.name,
  u.department,
  DATE_DIFF(CURRENT_DATE(), DATE(la.last_submission), DAY) as days_inactive
FROM last_activity la
JOIN `mind_analytics.user` u ON la.user = u.user_id
WHERE DATE_DIFF(CURRENT_DATE(), DATE(la.last_submission), DAY) >= 7
ORDER BY days_inactive DESC
```

**Business Significance:**
- Disengagement early warning
- Re-engagement campaign targeting
- Drop-out prevention

**Interpretation:**
- **7-14 days:** Normal break, gentle reminder
- **15-30 days:** Significant concern, outreach needed
- **>30 days:** Likely dropped out, intervention critical

---

### Progress Tracking Tab

#### 56. Weekly Submission Trends
**Definition:** Count of submissions per week over the semester.

**Calculation:**
```sql
SELECT 
  DATE_TRUNC(timestamp, WEEK) as week,
  COUNT(_id) as submissions,
  COUNT(DISTINCT user) as active_students,
  ROUND(AVG(final_score), 2) as avg_score
FROM `mind_analytics.grades`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 WEEK)
  AND final_score IS NOT NULL
GROUP BY week
ORDER BY week
```

**Business Significance:**
- Workload distribution validation
- Deadline impact analysis
- Engagement trend monitoring

**Pattern Recognition:**
- Spikes = Assignment deadlines
- Valleys = Exam weeks, breaks
- Declining trend = Disengagement concern

---

#### 57. Performance Trends Over Time
**Definition:** Average class score by week.

**Calculation:**
```sql
SELECT 
  DATE_TRUNC(timestamp, WEEK) as week,
  ROUND(AVG(final_score), 2) as avg_score,
  COUNT(DISTINCT user) as students
FROM `mind_analytics.grades`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 WEEK)
  AND final_score IS NOT NULL
GROUP BY week
ORDER BY week
```

**Business Significance:**
- Learning progress validation
- Teaching effectiveness over time
- Curriculum pacing assessment

**Interpretation:**
- **Upward trend:** Students improving (good)
- **Flat trend:** Consistent performance
- **Downward trend:** Investigate causes (fatigue, difficulty increase)

---

### Individual Student Tab

#### 58. Student Search and Lookup
**Definition:** Find specific student and display their complete profile.

**Calculation:**
```sql
-- Search by name
SELECT 
  u.user_id,
  u.name,
  u.department,
  u.cohort,
  COUNT(g._id) as total_submissions,
  ROUND(AVG(g.final_score), 2) as average_score,
  ROUND(MIN(g.final_score), 2) as lowest_score,
  ROUND(MAX(g.final_score), 2) as highest_score,
  MAX(g.timestamp) as last_activity
FROM `mind_analytics.user` u
LEFT JOIN `mind_analytics.grades` g ON u.user_id = g.user
WHERE LOWER(u.name) LIKE '%[search_term]%'
  AND u.role = 'student'
GROUP BY u.user_id, u.name, u.department, u.cohort
```

**Business Significance:**
- Personalized academic advising
- Individual intervention planning
- Student progress documentation

---

#### 59. Student Score Progression
**Definition:** Time series of individual student's scores across all submissions.

**Calculation:**
```sql
SELECT 
  g.timestamp,
  c.title as case_study,
  g.final_score,
  g.performance_summary
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.user = '[selected_user_id]'
  AND g.final_score IS NOT NULL
ORDER BY g.timestamp
```

**Visualization:** Line chart with trend line

**Business Significance:**
- Individual learning trajectory
- Intervention effectiveness validation
- Personalized goal setting

**Pattern Analysis:**
- **Upward trend:** Student improving
- **Plateau:** Need new challenges
- **Decline:** Investigate causes (personal issues, content difficulty)

---

#### 60. Student Percentile Rank
**Definition:** Student's rank relative to all students in class.

**Calculation:**
```sql
WITH student_avg AS (
  SELECT 
    user,
    AVG(final_score) as avg_score
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
),
ranked AS (
  SELECT 
    user,
    avg_score,
    PERCENT_RANK() OVER (ORDER BY avg_score) as percentile
  FROM student_avg
)
SELECT 
  ROUND(percentile * 100, 1) as percentile_rank
FROM ranked
WHERE user = '[selected_user_id]'
```

**Business Significance:**
- Relative performance indicator
- Recognition and awards
- Scholarship eligibility

**Interpretation:**
- **>90th percentile:** Top 10%, high achiever
- **50-90th percentile:** Above average
- **25-50th percentile:** Average
- **<25th percentile:** Below average, needs support

---

## Student Dashboard Metrics

### My Overview Tab

#### 61. Current Average Score
**Definition:** Student's mean score across all graded submissions.

**Calculation:**
```sql
SELECT ROUND(AVG(final_score), 2) as my_average
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

**Display:** Gauge chart (0-100 scale)

**Business Significance:**
- Personal performance summary
- Goal tracking baseline
- Self-assessment metric

**Color Coding:**
- **90-100:** Green (Excellent)
- **80-89:** Light green (Good)
- **70-79:** Yellow (Satisfactory)
- **<70:** Red (Needs Improvement)

---

#### 62. Total Submissions
**Definition:** Count of all graded case studies submitted.

**Calculation:**
```sql
SELECT COUNT(_id) as total_submissions
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

**Business Significance:**
- Engagement indicator
- Work completion metric
- Achievement tracking

---

#### 63. Class Percentile Rank
**Definition:** Student's rank relative to all peers.

**Calculation:**
```sql
WITH class_avg AS (
  SELECT 
    user,
    AVG(final_score) as avg_score
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
  GROUP BY user
),
my_rank AS (
  SELECT 
    user,
    avg_score,
    PERCENT_RANK() OVER (ORDER BY avg_score) as percentile
  FROM class_avg
)
SELECT ROUND(percentile * 100, 0) as my_percentile
FROM my_rank
WHERE user = '[current_user_id]'
```

**Interpretation:**
- **90-100:** Top 10%
- **75-90:** Top quarter
- **50-75:** Above average
- **25-50:** Below average
- **0-25:** Bottom quarter

---

#### 64. Comparison to Class Average
**Definition:** Difference between student's average and class average.

**Calculation:**
```sql
WITH my_avg AS (
  SELECT AVG(final_score) as avg
  FROM `mind_analytics.grades`
  WHERE user = '[current_user_id]'
    AND final_score IS NOT NULL
),
class_avg AS (
  SELECT AVG(final_score) as avg
  FROM `mind_analytics.grades`
  WHERE final_score IS NOT NULL
)
SELECT 
  my_avg.avg as my_score,
  class_avg.avg as class_score,
  ROUND(my_avg.avg - class_avg.avg, 2) as delta
FROM my_avg, class_avg
```

**Display:** Delta indicator (±X%)

**Interpretation:**
- **Positive delta:** Above class average
- **Zero delta:** At class average
- **Negative delta:** Below class average

---

#### 65. Recent Performance Trend
**Definition:** Comparison of recent average (last 5 submissions) vs. overall average.

**Calculation:**
```sql
WITH overall_avg AS (
  SELECT AVG(final_score) as avg
  FROM `mind_analytics.grades`
  WHERE user = '[current_user_id]'
    AND final_score IS NOT NULL
),
recent_avg AS (
  SELECT AVG(final_score) as avg
  FROM (
    SELECT final_score
    FROM `mind_analytics.grades`
    WHERE user = '[current_user_id]'
      AND final_score IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 5
  )
)
SELECT 
  recent_avg.avg - overall_avg.avg as trend
FROM recent_avg, overall_avg
```

**Interpretation:**
- **Positive trend:** Improving
- **Zero trend:** Stable
- **Negative trend:** Declining

---

### Progress Tracker Tab

#### 66. Score Progression Over Time
**Definition:** Time series of all student's scores.

**Calculation:**
```sql
SELECT 
  timestamp,
  final_score,
  c.title as case_study
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.user = '[current_user_id]'
  AND g.final_score IS NOT NULL
ORDER BY timestamp
```

**Visualization:** Line chart with:
- Actual scores (blue line)
- Trend line (red dashed)
- 80% target line (green horizontal)

**Business Significance:**
- Visual learning progress
- Motivational tool
- Goal setting baseline

---

#### 67. Daily Score Average
**Definition:** Mean score for submissions on each day.

**Calculation:**
```sql
SELECT 
  DATE(timestamp) as date,
  ROUND(AVG(final_score), 2) as daily_avg,
  COUNT(_id) as submissions
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
GROUP BY date
ORDER BY date
```

**Business Significance:**
- Study pattern identification
- Performance consistency tracking

---

### Case Studies Tab

#### 68. Performance by Case Study
**Definition:** Average score for each case study attempted.

**Calculation:**
```sql
SELECT 
  c.title as case_study,
  COUNT(g._id) as attempts,
  ROUND(AVG(g.final_score), 2) as avg_score,
  ROUND(MAX(g.final_score), 2) as best_score,
  MAX(g.timestamp) as last_attempt
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.user = '[current_user_id]'
  AND g.final_score IS NOT NULL
GROUP BY c.case_study_id, c.title
ORDER BY avg_score DESC
```

**Business Significance:**
- Identifies strengths (high scores)
- Identifies weaknesses (low scores)
- Retry opportunities (low best scores)

---

#### 69. Case Study Completion Status
**Definition:** List of all available case studies with completion indicators.

**Calculation:**
```sql
SELECT 
  c.title,
  CASE 
    WHEN g.user IS NOT NULL THEN 'Completed'
    ELSE 'Not Started'
  END as status,
  g.final_score
FROM `mind_analytics.casestudy` c
LEFT JOIN (
  SELECT DISTINCT case_study, user, MAX(final_score) as final_score
  FROM `mind_analytics.grades`
  WHERE user = '[current_user_id]'
    AND final_score IS NOT NULL
  GROUP BY case_study, user
) g ON c.case_study_id = g.case_study
ORDER BY c.title
```

**Business Significance:**
- Progress tracking
- Curriculum coverage
- Goal setting

---

### My Scores Tab

#### 70. All Submissions with Details
**Definition:** Complete history of graded submissions.

**Calculation:**
```sql
SELECT 
  g.timestamp,
  c.title as case_study,
  g.final_score,
  g.performance_summary,
  g.overall_summary
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.user = '[current_user_id]'
  AND g.final_score IS NOT NULL
ORDER BY g.timestamp DESC
```

**Display:** Sortable table with filters

**Business Significance:**
- Complete academic record
- Performance review
- Feedback access

---

#### 71. Personal Best Scores
**Definition:** Highest score achieved on each case study.

**Calculation:**
```sql
SELECT 
  c.title as case_study,
  MAX(g.final_score) as best_score,
  MAX(g.timestamp) as achieved_on
FROM `mind_analytics.grades` g
JOIN `mind_analytics.casestudy` c ON g.case_study = c.case_study_id
WHERE g.user = '[current_user_id]'
  AND g.final_score IS NOT NULL
GROUP BY c.case_study_id, c.title
ORDER BY best_score DESC
```

**Business Significance:**
- Achievement tracking
- Motivation tool
- Improvement opportunities

---

### Achievements Tab

#### 72. Excellence Badge (90%+ Average)
**Definition:** Awarded when student maintains ≥90% overall average.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN AVG(final_score) >= 90 THEN TRUE
    ELSE FALSE
  END as earned_excellence
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

**Display:** Gold badge with star icon

---

#### 73. High Performer Badge (80%+ Average)
**Definition:** Awarded when student maintains ≥80% overall average.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN AVG(final_score) >= 80 THEN TRUE
    ELSE FALSE
  END as earned_high_performer
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

**Display:** Silver badge

---

#### 74. Perfect Score Badge (100% on Any Assignment)
**Definition:** Awarded when student achieves 100% on at least one submission.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN MAX(final_score) >= 100 THEN TRUE
    ELSE FALSE
  END as earned_perfect
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

**Display:** Diamond badge

---

#### 75. Dedicated Learner Badge (50+ Submissions)
**Definition:** Awarded when student submits ≥50 graded assignments.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN COUNT(_id) >= 50 THEN TRUE
    ELSE FALSE
  END as earned_dedicated
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

---

#### 76. Active Student Badge (25+ Submissions)
**Definition:** Awarded at 25 submissions.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN COUNT(_id) >= 25 THEN TRUE
    ELSE FALSE
  END as earned_active
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

---

#### 77. Getting Started Badge (10+ Submissions)
**Definition:** Awarded at 10 submissions.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN COUNT(_id) >= 10 THEN TRUE
    ELSE FALSE
  END as earned_started
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

---

#### 78. Explorer Badge (5+ Different Cases)
**Definition:** Awarded when student attempts ≥5 different case studies.

**Calculation:**
```sql
SELECT 
  CASE 
    WHEN COUNT(DISTINCT case_study) >= 5 THEN TRUE
    ELSE FALSE
  END as earned_explorer
FROM `mind_analytics.grades`
WHERE user = '[current_user_id]'
  AND final_score IS NOT NULL
```

---

### Study Plan Tab

#### 79. Personalized Recommendations
**Definition:** AI-generated study suggestions based on performance patterns.

**Current Implementation:** Static recommendations based on score ranges

**Future Enhancement:** AI-powered analysis of:
- Performance trends
- Case study difficulties
- Learning style indicators
- Peer comparison

**Example Recommendations by Score:**
- **<70%:** Review fundamentals, seek tutoring
- **70-80%:** Focus on weak areas, practice more
- **80-90%:** Challenge yourself, try advanced cases
- **>90%:** Maintain excellence, mentor peers

---

## Future Metrics (Not Yet Available)

### Metrics Limited by Current Data

#### 80. Individual Rubric Scores
**Metric:** Communication, Comprehension, Critical Thinking scores separately

**Why Unavailable:**
Individual rubric components are calculated but **not stored** in BigQuery. Only the weighted `final_score` is available.

**Formula (Documented but Not Stored):**
```
final_score = (0.35 × communication) + (0.35 × comprehension) + (0.30 × critical_thinking)
```

**Business Value if Available:**
- Identify specific skill deficiencies
- Targeted intervention strategies
- Personalized learning paths
- Skill development tracking

**Implementation Requirements:**
- Add columns to `grades` table:
  - `communication NUMERIC`
  - `comprehension NUMERIC`
  - `critical_thinking NUMERIC`
- Update grading service to store individual scores
- Backfill historical data if possible

**Visualization Possibilities:**
- Radar charts showing all three dimensions
- Rubric-specific trend lines
- Peer comparison by rubric component
- Department averages by skill

---

#### 81. Attempt Number
**Metric:** Which attempt this is for a given case study

**Why Unavailable:**
`attempt` column documented but **does not exist** in actual BigQuery schema.

**Business Value if Available:**
- Track persistence (how many tries to succeed)
- Identify difficult cases (high retry rates)
- Learning curve analysis
- Mastery progression

**Implementation Requirements:**
- Add `attempt INTEGER` to `grades` table
- Update submission logic to increment attempt counter
- Handle edge cases (resets, partial completions)

**Analysis Possibilities:**
```sql
-- Average attempts to reach 80%
SELECT 
  c.title,
  AVG(attempt) as avg_attempts_to_pass
FROM grades g
JOIN casestudy c ON g.case_study = c.case_study_id
WHERE final_score >= 80
GROUP BY c.title
ORDER BY avg_attempts_to_pass DESC
```

---

#### 82. Time Spent on Case Study
**Metric:** Duration from case start to submission

**Why Unavailable:**
No timestamp for case study start, only submission timestamp.

**Business Value if Available:**
- Workload validation (is case too long?)
- Student engagement depth
- Procrastination patterns
- Case difficulty indicator

**Implementation Requirements:**
- Track `case_start_time` in `sessions` table
- Calculate duration: `submission_time - start_time`
- Filter out multi-day sessions (breaks, pauses)

**Analysis Possibilities:**
- Average time per case study
- Time vs. score correlation
- Student pace comparison (fast vs. slow learners)
- Identify cases that take too long

---

#### 83. Student Engagement Depth
**Metric:** Interaction quality beyond submission counts

**Why Unavailable:**
No logging of:
- Message counts with AI
- Questions asked
- Revisions made
- Resources accessed

**Business Value if Available:**
- Deep vs. shallow engagement
- Learning strategy identification
- Support needs prediction
- Retention indicators

**Implementation Requirements:**
- Log conversation message counts
- Track resource clicks
- Monitor revision history
- Capture help requests

**Possible Metrics:**
```sql
-- Engagement score
engagement_score = (
  (messages_sent × 1) +
  (resources_accessed × 2) +
  (revisions_made × 3)
) / submission_count
```

---

#### 84. Peer Collaboration Metrics
**Metric:** Study group participation, peer tutoring, discussion engagement

**Why Unavailable:**
Platform currently doesn't support collaboration features.

**Business Value if Available:**
- Social learning effectiveness
- Peer support networks
- Collaborative skill development
- Community building

**Implementation Requirements:**
- Add discussion forums
- Track group study sessions
- Monitor peer review participation
- Log collaborative projects

---

#### 85. Learning Resource Usage
**Metric:** Which supplemental materials students access

**Why Unavailable:**
No tracking of:
- Reading assignments viewed
- Video content watched
- External links clicked
- Help documentation accessed

**Business Value if Available:**
- Content effectiveness validation
- Resource optimization
- Personalized resource recommendations
- Support gap identification

**Implementation Requirements:**
- Add resource tracking table
- Log all content interactions
- Track time spent on resources
- Monitor resource-to-performance correlation

---

#### 86. Submission Quality Indicators
**Metric:** Beyond final score - response length, revision count, originality

**Why Unavailable:**
Only final score stored, no intermediate quality metrics.

**Business Value if Available:**
- Detect gaming/cheating
- Identify genuine understanding
- Assess effort levels
- Quality vs. quantity analysis

**Possible Indicators:**
- Response word count
- Unique vocabulary richness
- Citation usage
- Draft revision count
- Time from start to submission

---

#### 87. Predictive Success Metrics
**Metric:** Likelihood of course completion, final grade prediction

**Why Unavailable:**
Requires ML model trained on historical data.

**Business Value if Available:**
- Early intervention triggers
- Proactive support allocation
- Risk stratification
- Success probability

**Implementation Requirements:**
- Historical data (2+ semesters)
- Feature engineering (attendance, engagement, scores)
- ML model training
- Regular retraining pipeline

**Potential Features:**
- Early submission scores
- Attendance consistency
- Engagement trajectory
- Historical similar student outcomes

---

#### 88. Student Sentiment Analysis
**Metric:** Emotional state, frustration levels, confidence

**Why Unavailable:**
No NLP analysis of student responses or feedback.

**Business Value if Available:**
- Mental health support triggers
- Frustration detection
- Confidence building opportunities
- Personalized encouragement

**Implementation Requirements:**
- NLP sentiment analysis on submissions
- Optional mood check-ins
- Feedback form analysis
- Anonymous wellness surveys

---

#### 89. Career Outcome Correlation
**Metric:** How dashboard performance relates to post-graduation success

**Why Unavailable:**
No alumni tracking or outcome data collection.

**Business Value if Available:**
- Program effectiveness validation
- Curriculum-to-career alignment
- ROI demonstration
- Predictive career counseling

**Implementation Requirements:**
- Alumni survey system
- Employment outcome tracking
- Salary data collection (optional)
- Long-term study design (5+ years)

---

#### 90. Cross-Course Performance
**Metric:** Performance in MIND platform vs. other courses

**Why Unavailable:**
No integration with institutional LMS or grade systems.

**Business Value if Available:**
- Platform effectiveness validation
- Identify struggling students across all courses
- Comprehensive academic support
- Intervention coordination

**Implementation Requirements:**
- LMS integration (Canvas, Moodle, Blackboard)
- Data sharing agreements
- Privacy compliance (FERPA)
- Real-time data sync

---

### Metrics Requiring External Data

#### 91. Student Demographics Impact
**Metric:** Performance by age, gender, location, socioeconomic status

**Why Unavailable:**
Demographic data not collected (privacy, not required for function).

**Business Value if Available:**
- Equity analysis
- Support gap identification
- Targeted outreach
- Accessibility improvements

**Ethical Considerations:**
- Privacy concerns
- Bias amplification risks
- Regulatory compliance (GDPR, FERPA)
- Optional collection only

---

#### 92. Device and Connectivity Metrics
**Metric:** Student device types, internet quality, platform used

**Why Unavailable:**
No device fingerprinting or network quality monitoring.

**Business Value if Available:**
- Accessibility optimization
- Mobile experience improvements
- Identify tech barriers
- Digital divide analysis

**Implementation Requirements:**
- User agent logging
- Network latency tracking
- Browser performance monitoring
- Optional device surveys

---

#### 93. Cost-Effectiveness Analysis
**Metric:** Per-student cost, cost per learning outcome, ROI

**Why Unavailable:**
Requires institutional financial data and outcome definitions.

**Business Value if Available:**
- Budget justification
- Pricing optimization
- Value demonstration
- Resource allocation

**Data Needs:**
- Infrastructure costs
- Personnel costs
- Student outcomes
- Comparison benchmarks

---

## Metric Calculation Reference

### Common SQL Patterns

#### Safe Division (Avoid Division by Zero)
```sql
SAFE_DIVIDE(numerator, denominator)
-- OR
CASE WHEN denominator > 0 THEN numerator / denominator ELSE NULL END
```

#### Percentile Calculation
```sql
PERCENTILE_CONT(column, percentile_value) OVER (PARTITION BY group)
-- Example: PERCENTILE_CONT(score, 0.95) OVER () for P95
```

#### Date Comparisons
```sql
-- Last 7 days
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)

-- Last 30 days
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)

-- Current week
WHERE DATE_TRUNC(timestamp, WEEK) = DATE_TRUNC(CURRENT_DATE(), WEEK)
```

#### Moving Average (7-day)
```sql
AVG(score) OVER (
  ORDER BY date 
  ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) as moving_avg_7d
```

#### Year-over-Year Growth
```sql
WITH this_year AS (
  SELECT COUNT(*) as count
  FROM table
  WHERE EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE())
),
last_year AS (
  SELECT COUNT(*) as count
  FROM table
  WHERE EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE()) - 1
)
SELECT 
  ((this_year.count - last_year.count) * 100.0 / last_year.count) as yoy_growth
FROM this_year, last_year
```

---

## Glossary of Terms

**Active User:** User who has logged in or submitted work within a specified time period (default: 7 days)

**At-Risk Student:** Student whose average performance falls below institutional threshold (default: 70%)

**Class Average:** Mean final score across all students in a course or cohort

**Completion Rate:** Percentage of enrolled students who have submitted at least one graded assignment

**Engagement Rate:** Percentage of eligible students who have attempted a specific case study

**Final Score:** Weighted average of rubric components (communication 35%, comprehension 35%, critical thinking 30%)

**Latency:** Time between request initiation and response completion (measured in milliseconds)

**P50/P95/P99:** 50th, 95th, and 99th percentile metrics (value below which X% of observations fall)

**Percentile Rank:** Student's position relative to peers, expressed as percentage (e.g., 90th percentile = top 10%)

**Success Rate:** Percentage of API requests that complete without errors (HTTP 2xx responses)

**Token:** Unit of AI processing (roughly 0.75 English words)

**Uptime:** Percentage of time system is operational and accessible

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2024  
**Total Metrics Documented:** 93 (current) + extensive future metrics

This document serves as the definitive reference for all analytics metrics in the MIND Platform, providing technical teams, educators, and administrators with comprehensive understanding of what is measured, how it's calculated, and why it matters.
