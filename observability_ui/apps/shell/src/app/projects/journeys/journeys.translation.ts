export const journeysTranslations = {
  noJourneys: 'No journeys found.',
  relationships: 'Relationships',
  journeyRelationshipsTools: {
    addComponent: 'Add a new component',
    addDependency: 'Select exactly two components, in order, to add a dependency between them',
    delete: 'Remove selected elements from journey',
  },
  conditions: {
    batch: {
      title: 'Batch',
      description: 'A new instance is created when a run starts for this batch pipeline component'
    },
    default: {
      title: 'Default only',
      description: 'When there is no active instance, a new instance is created on receiving an event for the journey'
    },
    schedule: {
      title: 'Schedule',
      description: 'A new instance is created at the scheduled time'
    }
  }
};
