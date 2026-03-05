function [C_fade_cyc_sum11,C_fade_cyc_sum1,C_fade] = battery_lifetime_miner(mission_oneyear_SOC,Tbat_oney_wo,time);

t_years = 20;

mission_oneyear_SOC1 = fix(mission_oneyear_SOC);
time_cycle = time';

%% calendar ageing

mission_oneyear_idl1 = [];
mission_oneyear_idl2 = [];
mission_oneyear_idl3 = [];
cont = [];
cont(1)=0;
cont1 = 0;

for i=1:(length(mission_oneyear_SOC1))
    if i == length(mission_oneyear_SOC1);
        break
    else
    if (mission_oneyear_SOC1(i)== mission_oneyear_SOC1(i+1));
        cont1 = cont1+1;
    else
        cont1 = 0;
    end
    cont = [cont; cont1];
    if(cont(i+1)~=(cont(i)+1))
            mission_oneyear_idl1 = [mission_oneyear_idl1; cont(i)]; %% calendar time
            mission_oneyear_idl2 = [mission_oneyear_idl2; mission_oneyear_SOC1(i)];  %% SOC - calendar
            mission_oneyear_idl3 = [mission_oneyear_idl3; (i)];  %% SOC - time
    end
    end
end

Tbat_mean_wo = [];

for x = 1:length(mission_oneyear_idl1)
     Tmean = max(Tbat_oney_wo((mission_oneyear_idl3(x)-mission_oneyear_idl1(x)):(mission_oneyear_idl3(x))));
     Tbat_mean_wo = [Tbat_mean_wo;Tmean];
end

SOC_cal = repmat(mission_oneyear_idl2,t_years,1);
time_ca1 = repmat(mission_oneyear_idl1,t_years,1);
Tbat_mean_wo = repmat(Tbat_mean_wo,t_years,1);

C_fade_cyc_idl = ones(length(SOC_cal),1);
for i=1:length(SOC_cal)
    C_fade_c = 1.9775*(10^(-11))*exp(0.07511*(Tbat_mean_wo(i)+273.15))*1.639*(exp(0.007388*SOC_cal(i)))*((time_ca1(i)/(24*30*60))^0.8);
    C_fade_cyc_idl(i) = C_fade_c;
end

C_fade_cyc_sum1 = ones(length(SOC_cal),1);
C_fade_csum1 = 0;
for i=1:length(SOC_cal)
    C_fade_csum1 = ((C_fade_cyc_idl(i))^(1) + (C_fade_csum1)^(1));
    C_fade_cyc_sum1(i) = C_fade_csum1;
end

%% cycling

% Pegando os pontos de Vales e picos do ciclo de SOC
[pos_pks,pos_loc] = findpeaks(mission_oneyear_SOC1,time_cycle);
[neg_pks,neg_loc] = findpeaks(-mission_oneyear_SOC1,time_cycle);

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

RF = rainflow(mission_oneyear_SOCC,time);

%% cycling ageing

Tbat_mean_wo = ones(length(RF(1,:)),1);

for x = 1:length(RF(1,:))
     Tmean = max(Tbat_oney_wo(min((RF(4,x)),RF(5,x)):(max(RF(4,x),RF(5,x)))));
     Tbat_mean_wo(i) = Tmean;
end

Tbat_mean_wo = Tbat_mean_wo';

SOC_mean = repmat(RF(2,:)',t_years,1);
Tbat_mean_wo1 = repmat(Tbat_mean_wo',t_years,1);
DOD = repmat(RF(1,:)',t_years,1);

C_fade_cyc = ones(length(SOC_mean),1);
for i=1:length(SOC_mean)
    C_fade_c = 2.6418*exp(-0.01943*(SOC_mean(i)))*(0.004*exp(0.01705*(Tbat_mean_wo1(i)+273.15)))*(0.0123*(DOD(i))^(0.7162));
    C_fade_cyc(i) = C_fade_c;
end

C_fade_cyc_sum11 = ones(length(SOC_mean),1);
C_fade_csum1 = 0;

for i=1:length(SOC_mean)
    C_fade_csum1 = (C_fade_cyc(i) + (C_fade_csum1));
    C_fade_cyc_sum11(i) = C_fade_csum1;
end

%% Total lifetime

time_cyc = floor(length(C_fade_cyc_sum11)/(t_years*12));
time_cal = floor(length(C_fade_cyc_sum1)/(t_years*12));
C_fade = ones(t_years*12,1);

for i=1:(t_years*12)
    C_fade_1 = C_fade_cyc_sum1(time_cal*i)+0*C_fade_cyc_sum11(time_cyc*i);
    C_fade(i) = C_fade_1;
end

end