async function resolvePR({ github, context }) {
  const run = context.payload.workflow_run;

  // Fallback 0: direct from payload
  let pr = (run.pull_requests && run.pull_requests[0]) || null;

  // Fallback 1: by commit SHA (works for same-repo PRs)
  if (!pr) {
    const { owner, repo } = context.repo;
    const sha = run.head_sha;
    const { data: prsBySha } = await github.rest.repos.listPullRequestsAssociatedWithCommit({
      owner, repo, commit_sha: sha
    });
    pr = prsBySha[0] || null;
  }

  // Fallback 2: by head "owner:branch" (works for forks)
  if (!pr) {
    const headRepo = run.head_repository && run.head_repository.full_name; // "user/fork"
    const headBranch = run.head_branch;                                    // "feature"
    if (headRepo && headBranch) {
      const headParam = `${headRepo.split('/')[0]}:${headBranch}`;
      const { owner, repo } = context.repo;

      const { data: openPRs } = await github.rest.pulls.list({
        owner, repo, state: 'open', head: headParam, per_page: 1
      });
      pr = openPRs[0] || null;

      if (!pr) {
        const { data: closedPRs } = await github.rest.pulls.list({
          owner, repo, state: 'closed', head: headParam, per_page: 1
        });
        pr = closedPRs[0] || null;
      }
    }
  }

  if (!pr) throw new Error('Could not resolve PR for this workflow_run.');
  return Number(pr.number);
}

module.exports = { resolvePR };
