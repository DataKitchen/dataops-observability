import { CanActivateFn } from "@angular/router";
import { EntityStore } from "../entity";
import { inject } from "@angular/core";

export function resetStores(...stores: Array<typeof EntityStore<any, any>>): CanActivateFn {
    return () => {
        for (const storeType of stores) {
            inject(storeType).dispatch('reset');
        }
        return true;
    };
}