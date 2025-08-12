# Operational Excellence

Operational excellence (OE) is a commitment to build software correctly while consistently delivering a great customer experience. Along the way, operational excellence drives towards continuous integration and continuous delivery (CI/CD) by helping developers achieve high quality results consistently.

## Definitions
- Latency is the time it takes for a request to go from your client (in this case, the Canary) to your server (your API), and for the server to respond. In other words:
    - Latency = Request time + Processing time + Response time


## Design Principles

- Organize teams around business outcomes:
- Implement observability for actionable insights: - here we use services like Amazon CloudWatch, CloudTrail, and AWS X-Ray to monitor and analyze the performance of our applications and infrastructure.
- Safely automate where possible - applications, infrastructure, configuration, and procedures as code. You can have add safeguards, guardrails including rate control, error thresholds and approvals.
- Make frequent, small, reversible changes: 
- Refine operations procedures frequently
- Anticipate Failure - Maximize operational success by driving failure scenarios to understand the workload’s risk profile and its impact on your business outcomes.
- Learn from all operational events and metrics:


Operational Excellence is about more than just things “working” — it’s about observability, automation, preparedness, and continuous improvement.

It consists of the following key components:

