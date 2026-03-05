%% Battery Sizing
% UFMG Project 
% Rodrigo Cassio de Barros - 30/06/2020

%% Default
get(0,'factory');
set(0,'defaultAxesFontSize',14);
set(0,'defaultTextFontName', 'times');
set(0,'defaultAxesFontName', 'times');
clc; clear all;

%% Parâmetros da Bateria 
Cn = 111; %1h
Cr = 0.5;

  
%% Dados do projeto Fotovoltaico 
Pinv = 500e3;   % Potência do Inversor Trifásico 
Vdc = 800;      % Tensão do Barramento
Ebat = 9000; % Battery Energy  

%% Parâmetros de Projeto da bateria 
Wpv = Pinv; % Energy requirement (Wh)
Pbat = Pinv;  % Active power requirement (W) 

%% Variação de Tensões e SOC
SOC_max = 100;      % SOC maximo
SOC_min = 20;       % SOC mínimo 
Vb_soc_max = 89.5700;  % Vbat(SOC_max) (V)  
Vb_soc_min = 84.6170;  % Vbat(SOC_max) (V)

%% Total number of Battery 
% Energy Concept 
NT_ener = ceil(Wpv/(Ebat*(SOC_max-SOC_min)/100));

% Power Concept 
NT_Power = ceil(Pbat/(Vb_soc_min*Cn*Cr)); 

% Total Batteru number necessary
NT = max(NT_ener,NT_Power);

Ns = floor(Vdc/((Vb_soc_max)));

Np = ceil(NT/Ns);

NT_final = Ns*Np;


    

