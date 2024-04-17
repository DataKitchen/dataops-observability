export function listEnvVariableFormatter(value: string | null): string {
  const trimmed = value?.trim();
  if (!trimmed) {
    return '[]';
  }
  const trimmedArray = trimmed.split(',').map(item => item?.trim());
  return JSON.stringify(JSON.stringify(trimmedArray)).slice(1, -1);
}
