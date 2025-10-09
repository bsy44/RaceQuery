export interface Driver {
  driver: {
    driverId: string;
    fullName: string;
    nationality: string;
    code?: string;
    driverNumber?: string;
    dateOfBirth?: string;
  };
  team: string;
  wins: number;
  podium: number;
  points: string;
  points_diff: string;
  teamLogo?: string;
}
