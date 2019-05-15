clear
close all

ramp = csvread('ramp.csv');

% figure
% plot(ramp*1e6), grid

M4 = csvread('out_power_meter4_r_h.csv',9,1);
fid =fopen('out_power_meter4_r_h.csv');
tit = textscan(fid,'%s %*[^\n]','Delimiter',',');
fclose(fid);
time_S = char(tit{1}(10:end));
time4 = datetime(time_S(:,1:end-4),'InputFormat','yyyy-MM-dd HH:mm:ss');

P_4 = M4(:,1);
Q_4 = M4(:,2);

M12 = csvread('out_power_meter12_r_h.csv',9,1);
fid =fopen('out_power_meter12_r_h.csv');
tit = textscan(fid,'%s %*[^\n]','Delimiter',',');
fclose(fid);
time_S = char(tit{1}(10:end));
time12 = datetime(time_S(:,1:end-4),'InputFormat','yyyy-MM-dd HH:mm:ss');

P_12 = M12(:,1);
Q_12 = M12(:,2);

%%%%%%%%%%%%
% M4_h1 = csvread('out_power_meter4_r3_h1.csv',9,1);
% fid =fopen('out_power_meter4_r3_h1.csv');
% tit = textscan(fid,'%s %*[^\n]','Delimiter',',');
% fclose(fid);
% time_S_h1 = char(tit{1}(10:end));
% time4_h1 = datetime(time_S_h1(:,1:end-4),'InputFormat','yyyy-MM-dd HH:mm:ss');
% 
% P_4_h1 = M4_h1(:,1);
% Q_4_h1 = M4_h1(:,2);
% 
% M12_h1 = csvread('out_power_meter12_r3_h1.csv',9,1);
% fid =fopen('out_power_meter12_r3_h1.csv');
% tit = textscan(fid,'%s %*[^\n]','Delimiter',',');
% fclose(fid);
% time_S_h1 = char(tit{1}(10:end));
% time12_h1 = datetime(time_S(:,1:end-4),'InputFormat','yyyy-MM-dd HH:mm:ss');
% 
% P_12_h1 = M12_h1(:,1);
% Q_12_h1 = M12_h1(:,2);
%%%%%%%%%

Mb = csvread('LC_data0.csv',1,1);

Pb4 = Mb(1:24,2);       % Inverter output
Pb12 = Mb(25:48,2);     % Inverter output

PbT_a = (Pb4 + Pb12)*1e3;% Sum of nodes

N = length(time4);  Nc = N/24;
for i=1:1:Nc
    Matrix(:,i) = PbT_a;
end

PbT = reshape(Matrix',N,1);


%% Agregation per node

figure
subplot(2,1,1)
plot(time4, P_4/1e3), grid
ylabel('Power [KW]')
xlabel('Time [Hrs:Min]')
title(' Power - Node 4')
legend('Node 4')

subplot(2,1,2)
plot(time12, P_12/1e3), grid
ylabel('Power [KW]')
xlabel('Time [Hrs:Min]')
title(' Power - Node12 ')
legend('Node 12')

% subplot(2,1,2)
% plot(time4_h1, P_4_h1/1e3), grid
% ylabel('Power [KW]')
% xlabel('Time [Hrs:Min]')
% title(' Power - Node 4 - homes1')
% legend('Node 4')

% figure
% subplot(2,1,1)
% plot(time12, P_12/1e3), grid
% ylabel('Power [KW]')
% xlabel('Time [Hrs:Min]')
% title(' Power - Node12 ')
% legend('Node 12')
% 
% subplot(2,1,2)
% plot(time12_h1, P_12_h1/1e3), grid
% ylabel('Power [KW]')
% xlabel('Time [Hrs:Min]')
% title(' Power - Node12 - homes1')
% legend('Node 12')

P_T = (P_12 + P_4)/1e3;

% figure
% plot(time12, P_T,time12(1:60:end), ramp*1e3,'ro',time12(1:60:end), PbT_a*0.99), grid
% ylabel('Power [KW]')
% xlabel('Time [Hrs:Min]')
% title(' Total Power ')
% legend('Total power', 'Ramp','Tracking')

figure
plot(time12(1:60:end), ramp*1e3,'ro',time12(1:60:end), PbT_a), grid
ylabel('Power [KW]')
xlabel('Time [Hrs:Min]')
title(' Total Power ')
legend('Ramp','Tracking')

% figure
% plot(time12, P_T,time12, PbT), grid
% ylabel('Power [KW]')
% xlabel('Time [Hrs:Min]')
% title(' Total Power ')
% legend('Total power', 'Battery power')


figure
plot(time12, P_T - PbT,'r',time12(1:60:end), PbT_a*0.99, '-b'), grid
ylabel('Power [KW]')
xlabel('Time [Hrs:Min]')
% title(' Total Power ')
legend('Load power', 'Battery power')

figure
plot(time12, P_T, 'b', time12, P_T - PbT, 'r'), grid
ylabel('Power [KW]')
xlabel('Time [Hrs:Min]')
title(' Total Power ')
legend('Total power', 'Load power')

