import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinLvlComponent } from './basin-lvl.component';

describe('BasinLvlComponent', () => {
  let component: BasinLvlComponent;
  let fixture: ComponentFixture<BasinLvlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinLvlComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinLvlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
