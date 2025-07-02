# Understand the Core Concepts

In Google SecOps, Response Integration consists of Python scripts that are designed to execute third
party API and use the information as part of the Security Operation Center workflows.

In the Platform Response Integrations are available under Marketplace/Content Hub → Response
Integrations:

![response_integrations](/docs/resources/response_integrations/response_integrations.png)

Response Integration consists of the following script types:

- [Actions](/docs/response_integrations/content_deep_dive/actions.md)
- [Connectors](/docs/response_integrations/content_deep_dive/connectors.md)
- [Jobs](/docs/response_integrations/content_deep_dive/jobs.md)

**Action**—a Python script that is used to perform a simple activity. These scripts are then used
in playbooks to build an automated response. Key use cases are enrichment of Assets and IOCs,
performing triaging activities (Update Alert), remediation (Isolate Machines).

**Connector**—a Python script that runs continuously like a cron job. The main goal of the
connector is to ingest Alerts and Events from third party products into Google SecOps.

> **Note:** in Google SecOps you can also ingest data via SIEM Feed + Parser and in general, that’s
> the preferred method.

**Jobs**—a Python script that runs continuously, similar to the connector, but the use case for
this script is to synchronize information between Google SecOps and third Party Product. For
example,
if a comment was added to a Google SecOps Alert, to add the same comment to a third Party Alert.

You don’t need to have all script types inside the Response Integration for it to be considered
valid. As an example, in our official repository we have Response Integrations that only contain 2–3
actions and nothing else.
