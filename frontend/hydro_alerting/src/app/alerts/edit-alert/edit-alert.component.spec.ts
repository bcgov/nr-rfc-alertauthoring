import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditAlertComponent } from './edit-alert.component';

describe('EditAlertComponent', () => {
  let component: EditAlertComponent;
  let fixture: ComponentFixture<EditAlertComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditAlertComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EditAlertComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
