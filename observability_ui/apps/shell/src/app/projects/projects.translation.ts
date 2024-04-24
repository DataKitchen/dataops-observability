import { ComponentType, InstanceAlertType, RunAlertType } from '@observability-ui/core';

export const projectsTranslations = {
  projects: 'Projects',
  overview: 'Project Overview',
  componentTypeTag: {
    [ComponentType.BatchPipeline]: 'batch pipeline',
    [ComponentType.StreamingPipeline]: 'streaming pipeline',
    [ComponentType.Server]: 'server',
    [ComponentType.Dataset]: 'dataset',
  },
  instanceAlert: {
    [InstanceAlertType.LateStart]: 'Late Start',
    [InstanceAlertType.LateEnd]: 'Late End',
    [InstanceAlertType.Incomplete]: 'Incomplete',
    [InstanceAlertType.OutOfSequence]: 'Out of Sequence',
    [InstanceAlertType.DatasetNotReady]: 'Dataset not Ready'
  },
  mixedAlert: {
    [InstanceAlertType.LateStart]: 'Run: Late Start',
    [InstanceAlertType.LateEnd]: 'Run: Late End',
    [InstanceAlertType.Incomplete]: 'Journey: Incomplete',
    [InstanceAlertType.OutOfSequence]: 'Journey: Out of Sequence',
    [InstanceAlertType.DatasetNotReady]: 'Dataset: Not Ready',
    [InstanceAlertType.TestsFailed]: 'Tests: Failed',
    [InstanceAlertType.TestsHadWarnings]: 'Tests: Had Warnings',
    [RunAlertType.MissingRun]: 'Run: Missing',
    [RunAlertType.UnexpectedStatusChange]: 'Run: Unexpected Status Change',
    [RunAlertType.Failed]: 'Run: Failed',
    [RunAlertType.CompletedWithWarnings]: 'Run: Had Warnings',
  },
  emptyOverview: {
    noJourneys: {
      title: 'Create Data Journeys',
      description: 'Arrange components and build the relationships that deliver data analytic assets, then monitor the events as part of instances',
      button: 'Go to Journeys',
      learnMore: 'Data Journeys'
    },
    noEvents: {
      title: 'No journeys? Begin by connecting your Data Estate',
      description: 'Integrate your tools so events can be sent to DataOps Observability',
      button: 'Go to Integrations',
      learnMore: 'Get started with Observability'
    },
  },
  startType: {
    BATCH: 'Batch',
    SCHEDULED: 'Scheduled',
    DEFAULT: 'Default',
    PAYLOAD: 'Payload'
  },
};
