import type { AppConfig } from './lib/types';

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'El Video Bot',
  pageTitle: 'El Video Bot - Assistente Virtual',
  pageDescription: 'Assistente virtual em português com avatar animado',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: false,

  logo: '/lk-logo.svg',
  accent: '#002cf2',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#1fd5f9',
  startButtonText: 'Iniciar conversa',
};
