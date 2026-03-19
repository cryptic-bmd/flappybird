import type { ComponentType, JSX } from 'react';

import Game from '../pages/Game.tsx';
import Referral from '../pages/Referral.tsx';
import UserProfile from '../pages/UserProfile.tsx';


interface Route {
  path: string;
  Component: ComponentType;
  title?: string;
  icon?: JSX.Element;
}

export const routes: Route[] = [
  { path: '/', Component: Game },
  { path: '/profile', Component: UserProfile },
  { path: '/referrals', Component: Referral },
];
