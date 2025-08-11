const fs = require('fs');

async function postComment({ github, context, prNumber, title, reportPath }) {
  const body = fs.readFileSync(reportPath, 'utf8');
  const comment =
    `❌ **${title}**\n` +
    `<details>\n<summary>Click to view the full report</summary>\n\n---\n` +
    body + `\n</details>`;

  await github.rest.issues.createComment({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: prNumber,
    body: comment
  });
}

module.exports = { postComment };
