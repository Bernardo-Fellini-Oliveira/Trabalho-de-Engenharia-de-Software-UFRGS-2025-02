import axios, { type AxiosInstance } from 'axios';
import React, { useState, useEffect, use } from 'react';

// Usando a axios, além de deixar a declaração das requisições mais concisas definindo uma URL base e deixando evidente o método HTTP usado, 
// temos Conversão automática de JSON e Tratamento automático de erros na chamada da requisição




const api:AxiosInstance = axios.create({
      /*baseURL: import.meta.env.VITE_API_URL*/
      baseURL: 'http://localhost:8000/api' 

})


// insere o token automaticamente nas requests:
api.interceptors.request.use(config => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config;

    // Se access expirou, tenta refresh
    if (error?.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = await api.post("/auth/refresh");
        const newToken = refresh.data.access_token;

        localStorage.setItem("token", newToken);

        // atualiza o header da request original
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch {
        // Refresh falhou → logout
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);


export default api;