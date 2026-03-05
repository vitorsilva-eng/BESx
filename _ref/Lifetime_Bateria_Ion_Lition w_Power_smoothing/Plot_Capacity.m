clc;
clear all;
close all;

load('Cyc1.mat')
Cyc1 = Cyc;
load('Cyc2.mat')
Cyc2 = Cyc;
load('Cyc3.mat')
Cyc3 = Cyc;
load('Cyc4.mat')
Cyc4 = Cyc;

load('Ccal1.mat')
Ccal1 = Ccal;
load('Ccal2.mat')
Ccal2 = Ccal;
load('Ccal3.mat')
Ccal3 = Ccal;
load('Ccal4.mat')
Ccal4 = Ccal;

time = 1:length(Ccal);
time = time*30;
time = time/30;

figure(1)
subplot(2,1,1)
plot(time,Ccal1, 'k', 'LineWidth', 1.0);
hold on;
plot(time,Ccal2,'r', 'LineWidth', 1.0);
plot(time,Ccal3 ,'m', 'LineWidth', 1.0);
plot(time,Ccal4,'g', 'LineWidth', 1.0);


plot(time,Cyc1 ,  'k', 'LineWidth', 1.0);
plot(time,Cyc2,'r', 'LineWidth', 1.0);
plot(time,Cyc,'m', 'LineWidth', 1.0);
plot(time,Cyc4,'g', 'LineWidth', 1.0);

plot(time,Cyc1+Ccal1,'k', 'LineWidth', 1.0);
plot(time,Cyc2+ Ccal2, 'r', 'LineWidth', 1.0);
plot(time,Cyc3 + Ccal3 ,'m', 'LineWidth', 1.0);
plot(time,Cyc4 + Ccal4, 'g', 'LineWidth', 1.0);
xlabel ('Time(Month)')
ylabel('C fade (%)')
legend('Caso 1','Caso 2', 'Caso 3', 'Caso 4')
grid on;

subplot(2,1,2)
plot(time,Cyc1+Ccal1,'k', 'LineWidth', 1.0);
hold on;
grid on;
plot(time,Cyc2+ Ccal2, 'r', 'LineWidth', 1.0);
plot(time,Cyc3 + Ccal3 ,'m', 'LineWidth', 1.0);
plot(time,Cyc4 + Ccal4, 'g', 'LineWidth', 1.0);
xlabel ('Time(Month)')
ylim([19.5 21.5])
ylabel('C fade (%)')
grid on;

% figure(2)
% plot(time,Ccal1, 'k', 'LineWidth', 1.0);
% hold on;
% plot(time,Ccal2,'r', 'LineWidth', 1.0);
% plot(time,Ccal3 ,'b', 'LineWidth', 1.0);
% plot(time,Ccal4,'g', 'LineWidth', 1.0);
% xlabel ('Time(Month)')
% ylabel('C fade (%)')
% legend('Caso 1','Caso 2', 'Caso 3', 'Caso 4')
% grid on;
% % 
% figure(3)
% plot(time,Cyc1 ,  'k', 'LineWidth', 1.0);
% hold on;
% plot(time,Cyc2,'r', 'LineWidth', 1.0);
% plot(time,Cyc,'b', 'LineWidth', 1.0);
% plot(time,Cyc4,'g', 'LineWidth', 1.0);
% xlabel ('Time(Month)')
% ylabel('C fade (%)')
% legend('Caso 1','Caso 2', 'Caso 3', 'Caso 4')
% grid on;

% 
% figure(4)
% plot(time,Cyc1+Ccal1 );
% hold on
% plot(time,Cyc2+ Ccal2);
% plot(time,Cyc3 + Ccal3);
% plot(time,Cyc4 + Ccal4);
% grid on;
% 
% xlabel ('Time(Month)')
% ylabel('C fade (%)')
% legend('Caso 1','Caso 2', 'Caso 3', 'Caso 4')
% 
% 
