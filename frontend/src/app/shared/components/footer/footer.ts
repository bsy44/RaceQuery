import {Component, OnInit} from '@angular/core';
import {RouterLink, RouterLinkActive} from "@angular/router";

@Component({
  selector: 'app-footer',
    imports: [
        RouterLink,
        RouterLinkActive
    ],
  templateUrl: './footer.html',
  styleUrl: './footer.css'
})
export class Footer implements OnInit {
  currentYear: number = new Date().getFullYear();

  ngOnInit() {
    // Optionnel ici, currentYear est déjà initialisé
  }
}

