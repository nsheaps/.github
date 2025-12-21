# Workflow Run Metrics Collection

This guide explains how to collect and send GitHub Actions workflow metrics to observability platforms like Datadog, Prometheus, and New Relic.

## Overview

The `workflow-run-metrics.yml` workflow demonstrates how to:

1. Capture workflow run metadata using the `workflow_run` event
2. Extract timing and performance metrics
3. Send metrics to various observability platforms

## How It Works

### Trigger Event

The workflow uses the `workflow_run` event, which triggers when another workflow completes:

```yaml
on:
  workflow_run:
    workflows: ["CI", "Validate Workflows", "Ansible Test"]
    types:
      - completed
```

**Key Points:**
- Triggers after specified workflows complete (success or failure)
- Runs in the context of the default branch
- Has access to workflow run metadata

### Collected Metrics

The workflow collects:

- **Workflow Name**: Name of the completed workflow
- **Status**: `success`, `failure`, `cancelled`, `skipped`
- **Duration**: Time taken to complete (in seconds)
- **Run ID**: Unique identifier for the workflow run
- **Attempt Number**: Number of retry attempts
- **Branch**: Git branch the workflow ran on
- **Repository**: Full repository name
- **Timestamp**: When the workflow completed

## Integration Guides

### Datadog Integration

Datadog is a monitoring and analytics platform for infrastructure and applications.

#### Prerequisites

1. Create a [Datadog account](https://www.datadoghq.com/)
2. Generate an API key from [Datadog API Keys](https://app.datadoghq.com/organization-settings/api-keys)
3. Identify your Datadog site (e.g., `datadoghq.com`, `datadoghq.eu`)

#### Setup

1. Add secrets to your repository:
   ```
   DATADOG_API_KEY: Your Datadog API key
   DATADOG_SITE: Your Datadog site (optional, defaults to datadoghq.com)
   ```

2. The workflow sends metrics to the `/api/v2/series` endpoint:
   ```bash
   curl -X POST "https://api.${DD_SITE}/api/v2/series" \
     -H "DD-API-KEY: ${DD_API_KEY}" \
     -d '{"series": [...]}'
   ```

#### Available Metrics

- `github.workflow.duration`: Duration of workflow run in seconds
  - Tags: `workflow`, `status`, `repository`, `branch`

#### Viewing in Datadog

1. Navigate to [Metrics Explorer](https://app.datadoghq.com/metric/explorer)
2. Search for `github.workflow.duration`
3. Create dashboards and alerts based on these metrics

#### Example Dashboard Widgets

**Workflow Duration Over Time:**
```
Metric: github.workflow.duration
Aggregation: avg
Group by: workflow
```

**Workflow Success Rate:**
```
Metric: github.workflow.duration
Filter: status:success
vs
Metric: github.workflow.duration
Filter: status:failure
```

#### Additional Resources

- [Datadog Metrics API](https://docs.datadoghq.com/api/latest/metrics/)
- [Datadog Dashboards](https://docs.datadoghq.com/dashboards/)
- [Datadog GitHub Integration](https://docs.datadoghq.com/integrations/github/)

### Prometheus Integration

Prometheus is an open-source monitoring and alerting toolkit.

#### Prerequisites

1. Set up a [Prometheus Pushgateway](https://github.com/prometheus/pushgateway)
2. Ensure the Pushgateway is accessible from GitHub Actions runners
3. Note the Pushgateway URL (e.g., `http://pushgateway.example.com:9091`)

#### Setup

1. Add the Pushgateway URL to repository secrets:
   ```
   PROMETHEUS_PUSHGATEWAY_URL: http://your-pushgateway:9091
   ```

2. The workflow pushes metrics in Prometheus text format:
   ```bash
   cat <<EOF | curl --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/github_workflows"
   github_workflow_duration_seconds{...} 123
   github_workflow_status{...} 1
   EOF
   ```

#### Available Metrics

- `github_workflow_duration_seconds`: Duration in seconds
  - Labels: `workflow`, `status`, `branch`
- `github_workflow_status`: Binary status (1=success, 0=failure)
  - Labels: `workflow`, `branch`

#### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']
```

#### Example Queries

**Average workflow duration:**
```promql
avg(github_workflow_duration_seconds) by (workflow)
```

**Workflow success rate:**
```promql
sum(rate(github_workflow_status[5m])) by (workflow)
```

**Failed workflows in last hour:**
```promql
count(github_workflow_status{status="failure"} offset 1h)
```

#### Grafana Dashboards

Create Grafana dashboards using these metrics:

1. **Workflow Duration Panel:**
   - Query: `github_workflow_duration_seconds{workflow=~".*"}`
   - Visualization: Time series graph

2. **Success Rate Panel:**
   - Query: `rate(github_workflow_status[1h])`
   - Visualization: Gauge

#### Additional Resources

- [Prometheus Pushgateway](https://github.com/prometheus/pushgateway)
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Documentation](https://grafana.com/docs/)

### New Relic Integration

New Relic is an observability platform for monitoring applications and infrastructure.

#### Prerequisites

1. Create a [New Relic account](https://newrelic.com/)
2. Get your Account ID from [Account Settings](https://one.newrelic.com/admin-portal/api-keys/home)
3. Generate an Insert API Key (License Key) from [API Keys](https://one.newrelic.com/admin-portal/api-keys/home)

#### Setup

1. Add secrets to your repository:
   ```
   NEW_RELIC_API_KEY: Your Insert API Key
   NEW_RELIC_ACCOUNT_ID: Your Account ID
   ```

2. The workflow sends custom events to New Relic:
   ```bash
   curl -X POST "https://insights-collector.newrelic.com/v1/accounts/${ACCOUNT_ID}/events" \
     -H "X-Insert-Key: ${API_KEY}" \
     -d '[{"eventType": "GitHubWorkflowRun", ...}]'
   ```

#### Event Schema

Custom event: `GitHubWorkflowRun`

Attributes:
- `workflow`: Workflow name
- `status`: Completion status
- `duration`: Duration in seconds
- `repository`: Repository name
- `branch`: Git branch
- `runId`: Workflow run ID
- `attempt`: Retry attempt number
- `timestamp`: Unix timestamp

#### Querying in New Relic

Use NRQL (New Relic Query Language) to query events:

**Average workflow duration:**
```sql
SELECT average(duration) FROM GitHubWorkflowRun 
FACET workflow 
SINCE 1 day ago
```

**Failed workflows:**
```sql
SELECT count(*) FROM GitHubWorkflowRun 
WHERE status = 'failure' 
FACET workflow 
SINCE 1 week ago
```

**Slowest workflow runs:**
```sql
SELECT workflow, repository, duration 
FROM GitHubWorkflowRun 
ORDER BY duration DESC 
LIMIT 10
```

#### Creating Dashboards

1. Navigate to [Dashboards](https://one.newrelic.com/dashboards)
2. Create a new dashboard
3. Add widgets with NRQL queries

**Example Widget:**
```sql
SELECT average(duration) as 'Avg Duration', 
       max(duration) as 'Max Duration',
       count(*) as 'Total Runs'
FROM GitHubWorkflowRun 
FACET workflow
TIMESERIES
```

#### Setting Up Alerts

Create alerts for workflow failures:

1. Go to [Alerts & AI](https://one.newrelic.com/alerts-ai)
2. Create a new alert condition
3. Use NRQL:
   ```sql
   SELECT count(*) FROM GitHubWorkflowRun 
   WHERE status = 'failure'
   ```
4. Set threshold (e.g., > 3 failures in 5 minutes)

#### Additional Resources

- [New Relic Events API](https://docs.newrelic.com/docs/data-apis/ingest-apis/event-api/introduction-event-api/)
- [NRQL Query Language](https://docs.newrelic.com/docs/query-your-data/nrql-new-relic-query-language/get-started/introduction-nrql-new-relics-query-language/)
- [New Relic Dashboards](https://docs.newrelic.com/docs/query-your-data/explore-query-data/dashboards/introduction-dashboards/)

## Customization

### Adding More Metrics

Extend the workflow to collect additional metrics:

```yaml
- name: Get additional metrics
  id: extra_metrics
  run: |
    # Get job-level metrics
    JOBS_URL="${{ github.event.workflow_run.jobs_url }}"
    JOBS_DATA=$(curl -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" "$JOBS_URL")
    
    # Extract specific job durations
    echo "job_durations=$JOBS_DATA" >> $GITHUB_OUTPUT
```

### Adding Other Platforms

#### Splunk

```yaml
- name: Send to Splunk
  run: |
    curl -X POST https://http-inputs-splunk.example.com:8088/services/collector \
      -H "Authorization: Splunk ${{ secrets.SPLUNK_TOKEN }}" \
      -d '{"event": {...}}'
```

#### Elasticsearch

```yaml
- name: Send to Elasticsearch
  run: |
    curl -X POST https://elasticsearch.example.com:9200/github-workflows/_doc \
      -H "Content-Type: application/json" \
      -d '{"workflow": "...", ...}'
```

## Best Practices

### 1. Use Consistent Tags/Labels

Ensure all metrics use consistent naming:
- `workflow`: Workflow name
- `status`: Completion status
- `repository`: Full repo name
- `branch`: Git branch

### 2. Handle Secrets Safely

Always check if secrets are configured before using them:

```yaml
if: always() && env.DATADOG_API_KEY != ''
env:
  DATADOG_API_KEY: ${{ secrets.DATADOG_API_KEY }}
```

### 3. Include Error Handling

Handle API failures gracefully:

```yaml
run: |
  if ! curl ...; then
    echo "Failed to send metrics, continuing..."
  fi
```

### 4. Limit Metric Cardinality

Avoid high-cardinality labels:
- ❌ Don't use: commit SHA, PR number, timestamp
- ✅ Do use: workflow name, branch, status

### 5. Set Appropriate Retention

Configure retention policies in your observability platform to balance cost and data availability.

## Troubleshooting

### Metrics Not Appearing

1. Check repository secrets are configured
2. Verify API endpoints are accessible from GitHub Actions
3. Check workflow run logs for error messages
4. Validate API key permissions

### Incorrect Metric Values

1. Verify time calculations (timezone issues)
2. Check status mapping logic
3. Validate data types (string vs number)

### Rate Limiting

If you're hitting rate limits:
1. Batch metrics where possible
2. Add retry logic with exponential backoff
3. Consider sampling (e.g., only send metrics for main branch)

## Additional Resources

- [GitHub Actions Events](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [workflow_run Event Payload](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#workflow_run)
- [GitHub API - Workflow Runs](https://docs.github.com/en/rest/actions/workflow-runs)
