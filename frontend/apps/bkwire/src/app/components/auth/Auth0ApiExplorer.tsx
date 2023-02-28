import React from 'react';
import axios from 'axios';
import { Button } from '@mui/material';

export const Auth0ApiExplorer: React.VFC = () => {
  const customizeAuth0 = (domain: string, token: string, language: string) => {
    const headers = {
      'content-type': 'application/json',
      authorization: `Bearer ${token}`,
    };
    axios
      .request({
        method: 'PUT',
        url: `${domain}/api/v2/prompts/login/custom-text/${language}`,
        headers,
        data: {
          login: {
            title: 'Sign In',
            description: 'Corporate Bankruptcy - Business Impacts',
            footerText: "Don't have an account?",
            footerLinkText: 'Join Now',
          },
        },
      })
      .then((r) => {
        console.log(r.data);

        axios
          .request({
            method: 'PUT',
            url: `${domain}/api/v2/prompts/signup/custom-text/${language}`,
            headers,
            data: {
              signup: {
                title: 'Sign Up',
                description: 'Corporate Bankruptcy - Business Impacts',
                loginActionText: 'Already have an account?',
              },
            },
          })
          .then((r) => console.log(r.data))
          .catch((e) => console.error(e));
      })
      .catch((e) => console.error(e));
  };

  return (
    <Button
      onClick={() => {
        customizeAuth0('https://bkwire.us.auth0.com', '', 'en');
      }}
    >
      Customize Auth0 text
    </Button>
  );
};
