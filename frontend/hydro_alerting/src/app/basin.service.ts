import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BasinService {
  basins = [
    {
      id: 1,
      name: 'basin 1'
    },
    {
      id: 2,
      name: 'basin 2'
    },
    {
      id: 3,
      name: 'basin 33'
    },
    {
      id: 4,
      name: 'silly basin'
    }
  ];

  constructor() { }
}
