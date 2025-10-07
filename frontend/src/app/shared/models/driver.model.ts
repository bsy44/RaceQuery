export interface Driver {
  driver: {
    fullName: string;
    nationality: string
  };
  constructor: string[];
  points: string;
  points_diff: string;
  teamLogo?: string;
}
