import { Entity, WithId } from '../../entity';
import { AuthProvider } from '../auth/auth.model';

export interface Company extends Entity {
  company_code?: string;
  subdomain?: string;
  auth_provider?: AuthProvider;
}

export enum ActionType {
  SendEmail = 'SEND_EMAIL',
}

export interface Action extends WithId {
  name: string;
  action_impl: ActionType;
  action_args: any;
}

export interface EmailAction extends Action {
  action_impl: ActionType.SendEmail;
  action_args: {
    from_address: string;
    template: string;
    recipients: string[];
    smtp_config: {
      endpoint: string;
      port: number;
      username: string;
      password?: string;
    }
  }
}

export interface ActionsSearchFields {
  action_impl: string;
}
