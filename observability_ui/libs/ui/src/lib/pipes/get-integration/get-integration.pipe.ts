import { Pipe, PipeTransform } from '@angular/core';
import { IntegrationV1 } from '@observability-ui/core';

@Pipe({
  name: 'getIntegration',
  pure: true,
  standalone: true,
})
export class GetIngrationPipe implements PipeTransform {
  transform(integrations: IntegrationV1[], name: IntegrationV1['integration_name']): IntegrationV1 | undefined {
    if (!integrations || integrations.length <= 0 || !name) {
      return undefined;
    }

    return integrations.find(i => i.integration_name === name);
  }
}
