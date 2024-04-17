import { Menu } from '../components/sidenav-menu/sidenav-menu.model';
import { ProjectDisplayComponent } from './project-display/project-display.component';

export const ProjectsMenu: Array<Menu> = [
  {
    label: '',
    items: [
      { component: ProjectDisplayComponent },
      { icon: 'mdi-home', label: 'Overview', link: [ './overview' ] },
    ],
  },
  {
    label: 'Data Journeys',
    items: [
      { icon: 'mdi-map', label: 'Journeys', link: [ './journeys' ] },
      { icon: 'mdi-graph-outline', label: 'Instances', link: [ './instances' ] },
    ]
  },
  {
    label: 'Data Estate',
    items: [
      { icon: 'mdi-grain', label: 'Components', link: [ './components' ] },
      { icon: 'mdi-access-point', label: 'Events', link: [ './events' ] },
    ],
  },
  {
    label: 'Settings',
    items: [
      { icon: 'mdi-puzzle', label: 'Integrations', link: [ './integrations' ] },
      { icon: 'mdi-key', label: 'API Keys', link: [ './api-keys' ] },
      { icon: 'mdi-cog', label: 'Settings', link: [ './settings' ] },
    ]
  },
];
