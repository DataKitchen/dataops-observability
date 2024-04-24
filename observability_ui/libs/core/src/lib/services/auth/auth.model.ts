export const cookieKeys = {
  token: 'access_token',
};
export const cookiePath = '/';

export const localStorageKeys = {
  loginRedirect: 'login_redirect',
};

export enum AuthProviderType {
  Auth0 = 'auth0',
  OpenID = 'openId',
}

export interface AuthProvider {
  type: AuthProviderType;
  is_sso: boolean;
}

export interface Auth0AuthProvider extends AuthProvider {
  type: AuthProviderType.Auth0;
}

export interface OpenIDAuthProvider extends AuthProvider {
  type: AuthProviderType.OpenID;
  domain: string;
  client_id: string;
  client_secret: string;
}
