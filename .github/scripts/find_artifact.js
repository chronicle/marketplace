const fs = require('fs');

async function findAndDownloadArtifact({ github, context, artifactName, destZipPath }) {
  const { owner, repo } = context.repo;
  const run_id = context.payload.workflow_run.id;

  const { data: list } = await github.rest.actions.listWorkflowRunArtifacts({ owner, repo, run_id });
  const art = list.artifacts.find(a => a.name === artifactName);
  if (!art) throw new Error(`Artifact not found: ${artifactName}`);

  const { data } = await github.rest.actions.downloadArtifact({
    owner, repo, artifact_id: art.id, archive_format: 'zip'
  });
  fs.writeFileSync(destZipPath, Buffer.from(data));
  return true;
}

module.exports = { findAndDownloadArtifact };
