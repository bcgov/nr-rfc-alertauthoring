import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DeleteBasinLevelService {

  deleteEvent = new Subject<void>();

  constructor() { }

  emitDeleteEvent(basin_name: string) {
    console.log(`emitting delete event for ${basin_name}`);
    this.deleteEvent.next();
  }

}
