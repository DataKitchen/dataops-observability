type AggregatedSummary<T extends { status: string; count?: number }> = {
  [status in T['status']]?: number;
} & { TOTAL: number };

export function getCompleteSummary<T extends {
  status: string;
  count?: number
}>(summaries: T[] = []): AggregatedSummary<T> {
  const aggregate: AggregatedSummary<T> = { TOTAL: 0 };
  for (const item of summaries) {
    aggregate[item.status as T['status']] = (aggregate[item.status as T['status']] ?? 0) + (item.count ?? 1) as any;
    aggregate.TOTAL += item.count;
  }

  return aggregate;
}
