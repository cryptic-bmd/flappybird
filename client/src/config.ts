
export const PROJECT_NAME: string = import.meta.env.VITE_PROJECT_NAME ?? 'crash';
export const DEV: boolean = import.meta.env.VITE_DEV == "true";

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
export const SOCKET_URL: string = import.meta.env.VITE_SOCKET_URL ?? 'ws://localhost:8000';

export const REFERRAL_BONUS_MULTIPLIER: number = import.meta.env.VITE_REFERRAL_BONUS_MULTIPLIER ?? 0.25;

export const EMAIL_LINK = import.meta.env.VITE_EMAIL_LINK ?? "";
export const TELEGRAM_LINK = import.meta.env.VITE_TELEGRAM_LINK ?? "";
export const TELEGRAM_SUPPORT_LINK = import.meta.env.VITE_TELEGRAM_SUPPORT_LINK ?? "";
