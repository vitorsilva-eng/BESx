clc;
clear all;
close all;

%% Lifetime model - Power Smoothing

load_data1 = load('Irradiance_.mat');
Irradiance = load_data1.mission_oneyear1;

%% Filter PS
T = 10;
Tf = 180;
w = 60;
ksi = 0.707;

Ns = 30; %paineis em serie
Np = 85; %string em paralelo
Ef = 0.17; %eficiencia do painel
Ap = 2; %area painel em m2

%% PCS parametersL 

time = 60:60:(30*24*60*60);
time = time';
t_years = 1;
Nsb = 10;
Npb = 6;
SOCmin = 10; 
SOCmax = 90;
N = 1;
SOCi = 50;

%Pbess = 687.97e3; %(70%)
%Pbess = 903.18e3;  %(90%)
Pbess = 580.84e3;  %(60%)
%Pbess = 599.32e3;  %(61,73%)

b = [zeros(1,360) ones(1,780) zeros(1,300)]; % 0-6h charging 6-19h discharging  19-24h charging
c = [];

for i=1:30
    c = [c b];
end


%% Thermal Model LiFePO4
Rout = 9.12;
Rin = 3.273;
Cp = 73.2;
Temp=25+273.15;
Uac = 440;
%%
% Battery parameters
Rs = 0.017;
Ls = 1.9*10^(-8);
R1 = 0.003;
R2 = 0.06;
Q1 = 2.8; % Para o Modelo Zarq
Q2 = 890;  % Para o Modelo Zarq

% ZARC parameters
%Zarc1
w_zarc1 = (1/(Q1*R1))^(1/0.5);
Rc1 = 0.906*R1*(sin(0.5*pi*0.5/2))/(1+cos(0.5*pi*0.5/2));
Cc1 = 1/(w_zarc1*Rc1);
Rb1 = 0.670*(R1-Rc1)/2;
Rd1 = 0.670*(R1-Rc1)/2;
Cb1 = 1/(w_zarc1*10.886*Rb1);
Cd1 = 1/(w_zarc1*(1/10.886)*Rd1);
Ra1 = (R1-Rc1-Rb1-Rd1)/2;
Re1 = (R1-Rc1-Rb1-Rd1)/2;
Ca1 = 1/(w_zarc1*0.67^2*Ra1);
Ce1 = 1/(w_zarc1*(1/0.67^2)*Re1);

%Zarc2
w_zarc2 = (1/(Q2*R2))^(1/0.5);
Rc2 = 0.833*R2*(sin(0.8*pi*0.5/2))/(1+cos(0.8*pi*0.5/2));
Cc2 = 1/(w_zarc1*Rc2);
Rb2 = 0.804 *(R2-Rc2)/2;
Rd2 = 0.804 *(R2-Rc2)/2;
Cb2 = 1/(w_zarc2*4.675*Rb2);
Cd2 = 1/(w_zarc2*(1/4.675)*Rd2);
Ra2 = (R2-Rc2-Rb2-Rd2)/2;
Re2 = (R2-Rc2-Rb2-Rd2)/2;
Ca2 = 1/(w_zarc2*0.804^2*Ra2);
Ce2 = 1/(w_zarc2*(1/0.804^2)*Re2);

CAh = 78;
CAh0 = CAh;
CF = 0;

Ppvv = [];
Pbatt = [];
DPgg = [];
SOCC = [];

%% Degradation model
tic;
C_cyc = zeros(12*t_years,1);
C_cal = zeros(12*t_years,1);
CF_tot_acum = zeros(12*t_years,1);
RSS = zeros(12*t_years,1);
cahh = zeros(12*t_years,1);
missionn = zeros(12*t_years*43200,1);
C_cal_sum = 0;
C_cyc_sum = 0;
t_sum = 0;

OCV = [2.596 3.1490    3.2115    3.2200    3.2545    3.2810    3.2915    3.2950    3.2955    3.2960    3.2975    3.2995    3.3120 3.3335    3.3350    3.3345    3.3345    3.3345    3.36    3.41    3.445];
SOC = [0    0.0500    0.1000    0.1500    0.2000    0.2500    0.3000    0.3500    0.4000    0.4500    0.5000    0.5500 0.6000    0.6500    0.7000    0.7500    0.8000    0.8500    0.9000    0.9500    1.0000];

OCV = 4.*OCV;
OCV = 27.*OCV;

for t=1:t_years
    for i=1:(12)
        %Tbat_oney_wo = 30;
        mission_month_Irrad = Irradiance((1+(i-1)*43200):(43200*i));
        sim('SOCestimation2_1.slx');
        [Rs_i,R1_i,R2_i,Q1_i,Q2_i,C_cyc(i+(t-1)*12),C_cal(i+(t-1)*12),tt] = Lifetime_Degradation(mission_oneyear_SOC,Tbat,time,C_cyc_sum,C_cal_sum);
        C_cal_sum = C_cal(i+(t-1)*12);
        C_cyc_sum = C_cyc(i+(t-1)*12);
        CF_tot_acum(i+(t-1)*12) = C_cyc(i+(t-1)*12) + C_cal(i+(t-1)*12);
        CAh = CAh0 - CAh0*(1/100)*(C_cal_sum+C_cyc_sum);
        Rs = Rs + Rs_i;
        R1 = R1 + R1_i;
        R2 = R2 + R2_i;
        Q1 = Q1 - Q1_i;
        Q2 = Q2 - Q2_i;
        t_sum = t_sum + tt;
        
       RSS(i+(t-1)*12) = Rs_i/((1/100));
       cahh(i+(t-1)*12) = CAh;
       missionn((1+43200*((i-1)+(t-1)*12)):(43200*(i+(t-1)*12))) = mission_oneyear_Pg;
        
        w_zarc1 = (1/(Q1*R1))^(1/0.5);
        Rc1 = 0.906*R1*(sin(0.5*pi*0.5/2))/(1+cos(0.5*pi*0.5/2));
        Cc1 = 1/(w_zarc1*Rc1);
        Rb1 = 0.670*(R1-Rc1)/2;
        Rd1 = 0.670*(R1-Rc1)/2;
        Cb1 = 1/(w_zarc1*10.886*Rb1);
        Cd1 = 1/(w_zarc1*(1/10.886)*Rd1);
        Ra1 = (R1-Rc1-Rb1-Rd1)/2;
        Re1 = (R1-Rc1-Rb1-Rd1)/2;
        Ca1 = 1/(w_zarc1*0.67^2*Ra1);
        Ce1 = 1/(w_zarc1*(1/0.67^2)*Re1);
        
        w_zarc2 = (1/(Q2*R2))^(1/0.8);
        Rc2 = 0.833*R2*(sin(0.8*pi*0.5/2))/(1+cos(0.8*pi*0.5/2));
        Cc2 = 1/(w_zarc1*Rc2);
        Rb2 = 0.804*(R2-Rc2)/2;
        Rd2 = 0.804*(R2-Rc2)/2;
        Cb2 = 1/(w_zarc2*4.675*Rb2);
        Cd2 = 1/(w_zarc2*(1/4.675)*Rd2);
        Ra2 = (R2-Rc2-Rb2-Rd2)/2;
        Re2 = (R2-Rc2-Rb2-Rd2)/2;
        Ca2 = 1/(w_zarc2*0.804^2*Ra2);
        Ce2 = 1/(w_zarc2*(1/0.804^2)*Re2);
        i
        t
        Ppvv = [Ppvv; mission_oneyear_Ppv];
        Pbatt = [Pbatt; mission_oneyear_Pbat];
        DPgg = [DPgg; mission_oneyear_Pg];
        SOCC = [SOCC; mission_oneyear_SOC];

        end
end
toc;


%% Capacity fade - Plots

tt = 1/12:1/12:t_years;
ttt = 1:1:518400;
ttt1 = 1:1:43200;
figure
plot(tt,CF_tot_acum)
%xlim ([0 10.4]);
grid on
hold on
plot(tt,C_cal)
%xlim ([0 10.4]);
grid on
hold on
plot(tt,C_cyc)
%xlim ([0 10.4]);
ylim ([0 20]);
grid on
xlabel ('Years')
ylabel('C_f_a_d_e [%]')
legend('C_f_a_d_e_,_t_o_t_a_l','C_f_a_d_e_,_c_a_l','C_f_a_d_e_,_c_y_c')
%%
mission_dPg = [];
for i=1:12
    mission_dPg = [mission_dPg;missionn((1+43200*((i-1)+(1-1)*12)):(43200*(i+(1-1)*12)))];
end

figure
subplot(311)
plot(ttt,mission_dPg/1e3)
grid on
%ylim ([-110 110]);
xlim([0 length(ttt)])
xlabel ({'Month';'(a)'})
ylabel('\Delta P_g [kW/min]')
subplot(312)
plot(ttt1,mission_oneyear_SOC)
ylim ([0 100]);
xlim([0 length(ttt1)])
grid on
xlabel ({'Day';'(b)'})
ylabel('SOC [%]')
subplot(313)
plot(ttt1,mission_oneyear_Pbat/1000)
%ylim ([0 100]);
xlim([0 length(ttt1)])
grid on
xlabel ({'Day';'(c)'})
ylabel('P_B_E_S_S [kW]')
%%
ttd1= (1/(60)):(1/60):24*60*(1/60);
ttd = 1:1:24*60;
figure
subplot(211)
plot(ttd1,mission_oneyear_Pbat(ttd)/1e3,'LineWidth',1)
grid on
hold on 
plot(ttd1,mission_oneyear_Ppv(ttd)/1e3,'g','LineWidth',1)
hold on
plot(ttd1,mission_oneyear_Pgg(ttd)/1e3,'r','LineWidth',1)
xlim([0 24])
ylim([-600 1000])
xlabel ({'Hour';'(a)'})
ylabel('Power [kW]')
legend('BESS Power','PV Power','Power to grid');
% subplot(312)
% plot(ttd1,mission_oneyear_Pg(ttd)/1e3,'LineWidth',1)
% grid on
% xlim([0 24])
% ylim([-30 40])
% xlabel ({'Hour';'(b)'})
% ylabel('\Delta P_g [kW/min]')
subplot(212)
plot(ttd1,mission_oneyear_SOC(ttd),'LineWidth',1)
grid on
xlim([0 24])
xlabel ({'Hour';'(b)'})
ylabel('SOC [%]')

%%

subplot(212)
plot(ttt1,Tbat1)
ylim ([24 38]);
xlim([0 length(ttt1)])
grid on
xlabel ('Day')
ylabel('Battery Temperature [°C]')

%% pbess,ppv,Deltapg
temopo = 1:1:length(Pbatt);

subplot(321)
plot(temopo,Ppvv/1000)
ylim ([0 1100]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(a)'})
ylabel('P_P_V [kW]')

subplot(322)
plot(temopo,Ppvv/1000)
ylim ([680 1040]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(b)'})
ylabel('P_P_V [kW]')

subplot(323)
plot(temopo,Pbatt/1000)
ylim ([-650 650]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(c)'})
ylabel('P_B_E_S_S [kW]')

subplot(324)
plot(temopo,Pbatt/1000)
ylim ([450 600]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(d)'})
ylabel('P_B_E_S_S [kW]')

subplot(325)
plot(temopo,DPgg/1000)
ylim ([-105 105]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(e)'})
ylabel('\Delta P_g [kW/min]')

subplot(326)
plot(temopo,DPgg/1000)
ylim ([75 100]);
xlim([0 length(temopo)])
grid on
xlabel ({'Year';'(f)'})
ylabel('\Delta P_g [kW/min]')

print -depsc2 -painters FIG.eps;
