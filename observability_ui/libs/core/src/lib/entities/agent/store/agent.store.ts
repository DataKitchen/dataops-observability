import { makeStore } from '@microphi/store';
import { EntityStore } from '../../../entity';
import { Agent } from '../agent.model';
import { AgentService } from '../service/agent.service';
import { AgentState } from './agent.state';
import { AgentActions } from './agent.actions';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AgentStore extends EntityStore<AgentState, AgentActions, Agent> implements makeStore<AgentState, AgentActions> {

  constructor(protected service: AgentService) {
    super({
      list: [],
      total: 0,
    });
  }
}
