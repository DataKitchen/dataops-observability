import { Run, RunProcessedStatus } from '../models/runs.model';
import { TestStatus } from '../models';

interface RunsByComponent {
  [componentId: string]: Run[];
}

export function runsByComponent(runs: Run[]): RunsByComponent {
  const groups = {} as RunsByComponent;
  const result = runs.reduce((g, run) => {
    if (!g[run.pipeline.id]) {
      g[run.pipeline.id] = [];
    }
    g[run.pipeline.id].push(run);
    return g;
  }, groups);

  return result;
}

export function mostImportantStatus(runsOrTests: {
  status: RunProcessedStatus | TestStatus
}[], initial: RunProcessedStatus = RunProcessedStatus.Pending): RunProcessedStatus {
  return getRunProcessedStatus(runsOrTests
    .map((runOrTest) => runOrTest.status)
    .sort((a, b) => statusWeight[b] - statusWeight[a])[0] ?? initial);
}

export function getRunProcessedStatus(status: RunProcessedStatus | TestStatus): RunProcessedStatus {
  switch (status) {
    case TestStatus.Passed:
      return RunProcessedStatus.Completed;
    case TestStatus.Warning:
      return RunProcessedStatus.CompletedWithWarnings;
    case TestStatus.Failed:
      return RunProcessedStatus.Failed;
  }

  return status as RunProcessedStatus;
}

export const statusWeight: { [status in RunProcessedStatus | TestStatus]: number } = {
  [RunProcessedStatus.Failed]: 6,
  [TestStatus.Failed]: 6,
  [RunProcessedStatus.Missing]: 5,
  [RunProcessedStatus.CompletedWithWarnings]: 4,
  [TestStatus.Warning]: 4,
  [RunProcessedStatus.Running]: 3,
  [RunProcessedStatus.Pending]: 2,
  [RunProcessedStatus.Completed]: 1,
  [TestStatus.Passed]: 1
};

export function sortByStatusWeight(statusArray: { status: RunProcessedStatus | TestStatus }[]) {
  return statusArray?.sort((a, b) => statusWeight[a.status] - statusWeight[b.status]);
}
