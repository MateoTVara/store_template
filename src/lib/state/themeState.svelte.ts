import { LOCAL_STORAGE_KEYS } from "@lib/constants/localStorage";

type ThemeMode = 'light' | 'dark'

const getInitialTheme = (): ThemeMode => {
  if (typeof localStorage === 'undefined') return 'dark';
  const stored = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
  return stored === 'dark' ? 'dark' : 'light';
}

const theme: { mode: ThemeMode } = $state({
  mode: getInitialTheme(),
});

const applyTheme = (mode: ThemeMode) => {
  document.documentElement.classList.toggle('dark', mode === 'dark');
}

$effect.root(() => applyTheme(theme.mode) )

export const getTheme = () => theme.mode;

export const toggleTheme = () => {
  theme.mode = theme.mode === 'light' ? 'dark' : 'light';
  localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, theme.mode);
  applyTheme(theme.mode);
}