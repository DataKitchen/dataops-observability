import { TestgenTestType } from '../testgen-integration/testgen-integration.model';

export const instancesTranslation = {
  instances: 'instances',
  viewJourney: 'View Journey',
  instanceActive: {
    true: 'Active',
    false: 'Ended'
  },
  alertTooltipTitle: {
    WARNING: 'Warnings',
    ERROR: 'Errors'
  },
  thresholdLow: 'Min threshold',
  thresholdHigh: 'Max threshold',
  metricValue: 'Metric value',
  statuses: 'statuses',
  startType: {
    BATCH: 'Batch',
    SCHEDULED: 'Scheduled',
    DEFAULT: 'Default',
    PAYLOAD: 'Payload'
  },
  emptyList: {
    title: 'Monitor Data Journeys',
    description: 'An instance is the collection of events that occur for components in a Data Journey',
    button: 'Go to Journeys',
    learnMore: 'Data Journeys'
  },
  testgen: {
    title: 'Test Results from DataOps TestGen',
    testData: {
      title: 'Test Data',
      metricValue: 'Metric Value',
      table: 'Table',
      columns: 'Columns',
      testSuite: 'Test Suite',
      metricDescription: 'Metric Description',
    },
    testParams: {
      title: 'Test Parameters',
      min: 'Minimum',
      max: 'Maximum',
    },
    testType: {
      [TestgenTestType.AlphaTruncation]: 'Alpha Truncation',
      [TestgenTestType.AverageShift]: 'Average Shift',
      [TestgenTestType.ConstantMatch]: 'Constant Match',
      [TestgenTestType.DailyRecords]: 'Daily Records',
      [TestgenTestType.DecimalTruncation]: 'Decimal Truncation',
      [TestgenTestType.DateCount]: 'Date Count',
      [TestgenTestType.ValueCount]: 'Value Count',
      [TestgenTestType.EmailFormat]: 'Email Format',
      [TestgenTestType.PastDates]: 'Past Dates',
      [TestgenTestType.FutureYear]: 'Future Year',
      [TestgenTestType.NewShift]: 'New Shift',
      [TestgenTestType.AllValues]: 'All Values',
      [TestgenTestType.ValueMatch]: 'Value Match',
      [TestgenTestType.MinimumDate]: 'Minimum Date',
      [TestgenTestType.MinimumValue]: 'Minimum Value',
      [TestgenTestType.PercentMissing]: 'Percent Missing',
      [TestgenTestType.MonthlyRecords]: 'Monthly Records',
      [TestgenTestType.OutliersAbove]: 'Outliers Above',
      [TestgenTestType.OutliersBelow]: 'Outliers Below',
      [TestgenTestType.PatternMatch]: 'Pattern Match',
      [TestgenTestType.Recency]: 'Recency',
      [TestgenTestType.RequiredEntry]: 'Required Entry',
      [TestgenTestType.RowCount]: 'Row Count',
      [TestgenTestType.RowRange]: 'Row Range',
      [TestgenTestType.StreetAddress]: 'Street Address',
      [TestgenTestType.UniqueValues]: 'Unique Values',
      [TestgenTestType.PercentUnique]: 'Percent Unique',
      [TestgenTestType.USState]: 'US State',
      [TestgenTestType.WeeklyRecords]: 'Weekly Records',
      [TestgenTestType.CustomCondition]: 'Custom Condition',
      [TestgenTestType.AggregateMinimum]: 'Aggregate Minimum',
      [TestgenTestType.AggregateMatch]: 'Aggregate Match',
      [TestgenTestType.ComboMatch]: 'Combo Match',
      [TestgenTestType.PriorMatch]: 'Prior Match',
      [TestgenTestType.DistributionShift]: 'Distribution Shift',
      [TestgenTestType.TimeframeMinimum]: 'Timeframe Minimum',
      [TestgenTestType.TimeframeMatch]: 'Timeframe Match',
      [TestgenTestType.CustomTest]: 'Custom Test',
    },
    testDimension: {
      accuracy: 'Accuracy',
      completeness: 'Completeness',
      consistency: 'Consistency',
      timeliness: 'Timeliness',
      uniqueness: 'Uniqueness',
      validity: 'Validity',
    }
  },
};
