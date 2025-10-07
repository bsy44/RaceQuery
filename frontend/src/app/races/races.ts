import {HttpClient} from '@angular/common/http';
import {Component, OnInit} from '@angular/core';
import {COUNTRY_TO_ISO} from '../shared/nationalities';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {SelectorYears} from '../shared/components/selector-years/selector-years';

interface Race {
  Circuit: {
    Location: {
      country: string;
      locality: string;
    }
  }
  FirstPractice: {
    date: string;
  }
  date: string;
  raceName: string;
  round: string;
  sprint: boolean;
}

@Component({
  selector: 'app-races',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SelectorYears
  ],
  templateUrl: './races.html',
  styleUrl: './races.css'
})

export class Races implements OnInit{
  years: number [] = [];
  raceList: any[] = [];
  selectedYear: number = new Date().getFullYear();

  constructor(private http:HttpClient) {}

  ngOnInit() {
    const currentYear = new Date().getFullYear();
    this.years = Array.from({length: currentYear - 2024 + 1}, (_, i) => 2024 + i).reverse();

    this.getRaces();
  }

  getRaces() {
    this.http.get(`http://127.0.0.1:5000/races/${this.selectedYear}`).subscribe((result: any) => {
      this.raceList = (result || []).map((race: Race, i: number) => {
        const circuit = race.Circuit;
        const location = circuit?.Location;


        const formatDateRange = (startStr: string | null | undefined, endStr: string | null | undefined): string => {
          if (!startStr || !endStr) return '—';

          const start = new Date(startStr.replace(' ', 'T'));
          const end = new Date(endStr.replace(' ', 'T'));

          if (isNaN(start.getTime()) || isNaN(end.getTime())) return '—';

          const startDay = start.getDate().toString().padStart(2, '0');
          const endDay = end.getDate().toString().padStart(2, '0');

          const month = end.toLocaleDateString('fr-FR', { month: 'short' })
            .replace('.', '')
            .toUpperCase();
          return `${startDay} - ${endDay} ${month}`;
        };

        return {
          round: race.round || i + 1,
          country: location?.country,
          raceName: race.raceName,
          locality: location?.locality,
          date: formatDateRange(race.FirstPractice?.date, race.date)
        }
      });
    });
  }

  getFlagClass(country: string): string {
    return  COUNTRY_TO_ISO[country] || 'xx';
  }
}
