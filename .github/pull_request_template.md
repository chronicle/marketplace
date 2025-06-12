## MUST-DOs (Essential for Security and Compliance):

- [ ] Origin in Buganizer: All work must have originated from a Buganizer ticket, even
  if it's a simple fix.
- [ ] No PII/Sensitive Data: The PR title, description, and any associated comments on
  GitHub MUST NOT contain any Personally Identifiable Information (PII) like customer
  names, email addresses, or any other data that could identify an individual.
- [ ] No Internal-Only Data: The PR title, description, and any associated comments on
  GitHub MUST NOT contain internal-only code examples, configurations, URLs, or any
  other sensitive internal data.
- [ ] Public-Facing Language: Ensure all language in the PR is suitable for a public
  audience. Avoid internal jargon unless it's widely understood in the open-source
  community.
- [ ] Link to Buganizer: Clearly and consistently include the Buganizer ticket
  number/link in the PR description (e.g., "Internal Buganizer ID: 123456789" or "
  Related Buganizer: go/buganizer/123456789"). This is crucial for internal
  traceability.
- [ ] Standardized Title: Use a clear, concise, and public-facing PR title. Consider
  including a Buganizer reference like [Buganizer #123456789] Public-facing summary of
  change.
- [ ] Code Sanitization: Double-check that any code examples or test data included in
  the PR are generic and do not expose internal system details or customer data.

## SHOULD-DOs (Best Practices for Collaboration and Efficiency):

- [ ] Link to GitHub Issue (if applicable): If a corresponding GitHub issue exists, link
  the PR to it in the description (e.g., Closes #XYZ).
- [ ] Concise Summary: Provide a brief, public-facing summary of the changes in the PR
  description.
- [ ] Problem/Solution: Briefly explain the problem the PR solves and the solution
  implemented, from a public perspective.
- [ ] Testing Instructions (Public): If relevant, provide public-facing instructions on
  how to test the changes.
- [ ] Screenshots/GIFs (if applicable): If the change has a visual impact, include
  anonymized screenshots or GIFs.
- [ ] Self-Review: Always perform a self-review of your PR before requesting reviews.
- [ ] Appropriate Labels: Apply relevant GitHub labels to your PR (e.g., bug, feature,
  refactor).

## MUST-NOT-DOs (Critical Prohibitions):

- [ ] NEVER copy and paste Buganizer internal comments or descriptions directly into a
  GitHub PR or issue.
- [ ] DO NOT discuss PII or sensitive internal details in GitHub comments or
  discussions. Redirect internal discussions to the linked Buganizer ticket.
- [ ] DO NOT include private API keys, credentials, or other sensitive configuration
  details in the code or PR description.
- [ ] DO NOT commit internal-only tools, scripts, or documentation to the public
  repository.