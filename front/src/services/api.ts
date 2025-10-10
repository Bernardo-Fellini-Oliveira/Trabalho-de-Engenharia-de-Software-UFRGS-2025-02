import axios, { type AxiosInstance } from 'axios';
import React, { useState, useEffect, use } from 'react';

// Usando a axios, além de deixar a declaração das requisições mais concisas definindo uma URL base e deixando evidente o método HTTP usado, 
// temos Conversão automática de JSON e Tratamento automático de erros na chamada da requisição




const api:AxiosInstance = axios.create({
      /*baseURL: import.meta.env.VITE_API_URL*/
      baseURL: 'https://www.inf.ufrgs.br/~ikscarvalho/eng-software' 

})


export default api;