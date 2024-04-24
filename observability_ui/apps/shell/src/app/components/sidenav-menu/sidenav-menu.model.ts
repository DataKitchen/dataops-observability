import { ComponentType } from '@angular/cdk/overlay';

export interface Menu {
  label: string;
  items: (MenuItemLink|MenuItemComponent)[];
}

export interface MenuItemLink {
  icon: string;
  label: string;
  link: any[];
}

export interface MenuItemComponent {
  component: ComponentType<any>
}
