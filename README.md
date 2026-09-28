*Mod. 321 Verteilte Systeme*

**Setup Anleitung:**

1. Pull the GitHub Repo
git clone https://github.com/Faraftic/verteilte-systeme

2. Open the Project in VSCode and connect to the JoyPi via SSH
Bottom left in VSC -> Open a remote Window -> Connect to Host -> Nils@NCRasp05 -> Enter Password -> Open Project Folder Mod321

3. Start Dashboard
Open the Console with CTRL + J and navigate to Nils@NCRasp05:~/Mod321/dashboard
sudo docker compose up -d --build

4. Start MQTT
Open the Console with CTRL + J and navigate to Nils@NCRasp05:~/Mod321/mosquitto
sudo docker compose up -d --build

5. Start Sensor-Api
Open the Console with CTRL + J and navigate to Nils@NCRasp05:~/Mod321/sensor-api
sudo docker compose up -d --build

6. Start System-Monitoring
Open the Console with CTRL + J and navigate to Nils@NCRasp05:~/Mod321/system-monitoring
sudo docker compose up -d --build


**Frontend-Endpoints**

**Sensor-APIs**
http://ncrasp05:8080/api/air
http://ncrasp05:8080/api/light
http://ncrasp05:8080/api/sound

**Grafana**
http://ncrasp:3000

**Dashboard**
http://ncrasp05:80

