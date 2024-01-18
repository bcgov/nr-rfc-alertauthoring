import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinAddFormComponent } from './basin-add-form.component';

describe('BasinAddFormComponent', () => {
  let component: BasinAddFormComponent;
  let fixture: ComponentFixture<BasinAddFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinAddFormComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinAddFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
