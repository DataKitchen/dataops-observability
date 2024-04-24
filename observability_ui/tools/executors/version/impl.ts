import type { ExecutorContext } from '@nrwl/devkit';
import { exec } from 'child_process';
import { promisify } from 'util';
import { replace } from 'replace-json-property';
import { logger } from '@nrwl/devkit';


export default async function versionExecutor(
  options: void,
  context: ExecutorContext
): Promise<{ success: boolean }> {

  const { stdout, stderr } = await promisify(exec)(
    `lerna ls --json`
  );

  const versions = JSON.parse(stdout);
  const apps = {};

  if (Array.isArray(versions)) {
    logger.info(`Found ${versions.length} packages.`);
    for (const v of versions) {
      logger.info(`${v.name}: ${v.version}`);
      apps[v.name] = v.version;
    }
  }

  logger.info('Updating ngsw-config.json');
  replace(`${context.root}/apps/shell/ngsw-config.json`, 'appData', apps, {
    silent: true,
  });
  logger.info('Done!');

  const success = stderr.includes('lerna success');
  return { success };
}
