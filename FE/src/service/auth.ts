
const AUTH_KEY = "lexgen.token"
export const AUTHORIZATION_HEADER_NAME = 'X-Authorization';

export const setAuthToken = (token: string) => {
  localStorage.setItem(AUTH_KEY, token);
};

const getAuthToken = () => {
  return typeof window !== 'undefined' ? localStorage.getItem(AUTH_KEY) : '';
};

export const resetAuthToken = () => {
  localStorage.removeItem(AUTH_KEY);
};

export const getAuthorizationHeaderValue = () => {
  const token = getAuthToken();
  return `Bearer ${token}`;
};

export const hasAuthToken = () => {
  return !!getAuthToken();
};
