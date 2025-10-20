import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {ActivatedRoute, Router} from '@angular/router';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-race-details',
  templateUrl: './race-detail.html',
  imports: [DatePipe],
  styleUrls: ['./race-detail.css']
})
export class RaceDetail implements OnInit {
  round!: number;
  season!: number;
  raceData: any;

  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    const nav = this.router.lastSuccessfulNavigation;
    this.round = nav?.extras?.state?.['round'] || null;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    console.log()

    this.getRaceDetail();
  }

  goBack() {
    window.history.back();
  }

  getRaceDetail() {
    this.httpClient.get<any[]>(`http://127.0.0.1:5000/events/${this.season}/${this.round}`)
      .subscribe((result: any) => {

        const formatDateRange = (
          sessions: any[] | undefined,
          raceEndStr: string | null | undefined
        ): string => {
          if (!sessions || sessions.length === 0) return '—';

          const fp1 = sessions.find(s => s.name?.toLowerCase().includes('fp1')) || sessions[0];
          const startStr = fp1?.local_date;
          const endStr = raceEndStr;

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

        this.raceData =  {
          circuitName: result.circuit_name,
          country: result.country,
          eventDate: formatDateRange(result.sessions, result.event_date),
          location: result.location,
          round: result.round,
          season: result.season,
          gpName: result.short_name,
          sessions: result.sessions,
          eventFormat: result.event_format
        };
      });
  }

  getSessionClass(name: string): string {
    const n = name.toLowerCase();
    if (n.includes('practice')) return 'free-practice';
    if (n.includes('sprint') || n.includes('sprint qualifying')) return 'sprint';
    if (n.includes('qualifying')) return 'quali';
    if (n.includes('race')) return 'race';
    return '';
  }

  translateSessionName(sessionName: string, index: number): string {
    const name = sessionName.toLowerCase();

    if (name.includes('practice')) {
      return `Essais Libres ${index + 1}`;
    }
    if (name.includes('sprint qualifying')) return 'Qualification Sprint';
    if (name.includes('qualifying')) return 'Qualification';
    if (name.includes('sprint')) return 'Sprint';
    if (name.includes('race')) return 'Course';

    return sessionName;
  }

}
