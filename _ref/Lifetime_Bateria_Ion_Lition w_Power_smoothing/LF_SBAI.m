
function [C_fade_cyc,C_fade_Cal,tt]= Lifetime_Degradation(mission_oneyear_SOC,Tbat,time_cycle,C_fade_cyc,C_fade_Cal)

%% Authors: William Caires and Rodrigo Barros 28/04/2020.

% This function is responsible to return the capacity fade for the
% calendar a cycling aging in one month of mission profile. 

% ------Inputs-----: 
% mission_oneyear_SOC: SOC mission profile (one month);
% Tbat_oney_wo: Temperature mission profile (one month);
% time_cycle: The time vector of the above mission profiles;

%-----Outputs------:

% C_fade_cyc: Capacity Fade for the Cycling Aging;
% C_fade_Cal: Capacity Fade for the Calendar Aging; 

% Also, some optionals outputs from the cycling stress are proposed:
% SOC_cycling: SOC mean values; 
% DOD_cycling: DOD values; 
% nc_cycling: number of cycling 


%%---------------- Calendar ageing------------------%%

mission_oneyear_idl1 = [];
mission_oneyear_idl2 = [];
mission_oneyear_idl3 = [];
cont = [];
cont(1)=0;
cont1 = 0;

for i=1:(length(mission_oneyear_SOC))
    if i == length(mission_oneyear_SOC);
        break
    else
    if (mission_oneyear_SOC(i)== mission_oneyear_SOC(i+1));
        cont1 = cont1+1;
    else
        cont1 = 0;
    end
    cont = [cont; cont1];
    if(cont(i+1)~=(cont(i)+1))
            mission_oneyear_idl1 = [mission_oneyear_idl1; cont(i)]; %% calendar time
            mission_oneyear_idl2 = [mission_oneyear_idl2; mission_oneyear_SOC(i)];  %% SOC - calendar
            mission_oneyear_idl3 = [mission_oneyear_idl3; (i)];  %% SOC - time
    end
    end
end

Tbat_mean_wo = [];

for x = 1:length(mission_oneyear_idl1)
     Tmean = (Tbat(x)-273.15);
     Tmean = 35;
     Tbat_mean_wo = [Tbat_mean_wo;Tmean];
end

SOC_cal = mission_oneyear_idl2;
time_ca1 = mission_oneyear_idl1;

tt = sum(time_ca1);

C_fade_cal_sum = ones(length(SOC_cal),1); 

for i=1:length(SOC_cal)
    C_fade_c = 1.9775*(10^(-11))*exp(0.07511*(Tbat_mean_wo(i)+273.15))*1.639*(exp(0.007388*SOC_cal(i)))*((time_ca1(i)/(24*30*60/5))^0.8);
    C_fade_cal_sum(i) = C_fade_c;
end

C_fade_cal_sum1 = zeros(length(SOC_cal),1);
C_cal_sum = C_fade_Cal;

for i=1:length(SOC_cal)
    C_cal_sum = ((C_fade_cal_sum(i))^(10/8) + (C_cal_sum)^(10/8))^(0.8);
    C_fade_cal_sum1(i) = C_cal_sum;
end

C_fade_Cal = C_fade_cal_sum1(length(SOC_cal));


%%----------------------- cycling Ageing--------------------%% 

% Pegando os pontos de Vales e picos do ciclo de SOC
[pos_pks,pos_loc] = findpeaks(mission_oneyear_SOC,time_cycle);
[neg_pks,neg_loc] = findpeaks(-mission_oneyear_SOC,time_cycle);

pos_loc = pos_loc';
neg_loc = neg_loc';
pos_pks = pos_pks';
neg_pks = neg_pks';

% Reconstruindo do sinal do ciclo de SOC a a partir dos picos e Vales
time = [pos_loc neg_loc];
peak_total = [pos_pks neg_pks];

for i =1:1:length(time)
    if  peak_total(i) < 0
         peak_total(i) =   -1* peak_total(i);
    end 
end 

for i =1:1:length(time)
   for j = (i + 1):1:length(time)
          if time(i) > time(j)
              
              aux1 = time(i);
              aux2 = peak_total(i);
              
              time(i) = time(j);
              peak_total(i) = peak_total(j);
              
              time(j) = aux1;
              peak_total(j) = aux2;                                         
                     
          end 
   end 
end

mission_oneyear_SOCC = peak_total;

% Taking the Battery temperature in the cycling process

RF = rainflow(mission_oneyear_SOCC,time);
Tbat_mean_wo = ones(length(RF(1,:)),1);

for x = 1:length(RF(1,:))
     Tmean = (Tbat(x)-273.15);
     Tmean = 35;
     Tbat_mean_wo(i) = Tmean;
end

Tb_cycling = Tbat_mean_wo';

%  Taking the SOC_cycling, DOD_cycling, nc_Cycing 
% y = [RF(3,:);RF(1,:);RF(2,:)];
% [nc_cycling,DOD_cycling,SOC_cycling]= rfmatrix(y);
SOC_cycling = RF(2,:);
DOD_cycling = RF(1,:);

%% Aging for the cycle 
     
% C_fade_cyc_sum = 0; 
% for j=1:length(DOD_cycling)   
%     for i=1:length(SOC_cycling)
%         C_fade_c = 2.6418*exp(-0.01943*(SOC_cycling(i)))*(0.004*exp(0.01705*(30+273.15)))*(0.0123*(DOD_cycling(j))^(0.7162))*(nc_cycling(i,j)^0.5);
%         C_fade_cyc_sum = C_fade_cyc_sum + C_fade_c;
%     end
% end
% C_fade_cyc = C_fade_cyc_sum;

C_fade_cyc1 = ones(length(SOC_cycling),1); 
for i=1:length(SOC_cycling)
    C_fade_c = 2.6418*exp(-0.01943*(SOC_cycling(i)))*(0.004*exp(0.01705*(Tb_cycling(i)+273.15)))*(0.0123*(DOD_cycling(i))^(0.7162));
    C_fade_cyc1(i) = C_fade_c;
end

C_fade_cyc_sum1 = zeros(length(SOC_cycling),1);
C_cyc_sum = C_fade_cyc;
for i=1:length(SOC_cycling)
    C_cyc_sum = sqrt((C_fade_cyc1(i))^(2) + (C_cyc_sum)^(2));
    C_fade_cyc_sum1(i) = C_cyc_sum;
end

C_fade_cyc = C_fade_cyc_sum1(length(SOC_cycling));



end 