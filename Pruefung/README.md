*Mod. 321 Verteilte Systeme*

In this manual it's described how to get the project onto an JoyPi 

**Setup Instruction:**

1. Pull the GitHub Repo
git clone https://github.com/Faraftic/verteilte-systeme

-If you dont have access to the GitRepo you can just copy the folder onto your JoyPi via SCP

2. Open the Project in VSCode and connect to the JoyPi via SSH
-Note: Replace the User@Hostname with yours and also edit the Path to the full Directory path where you cloned the Repo into

Bottom left in VSC -> Open a remote Window -> Connect to Host -> Nils@NCRasp05 -> Enter Password -> Open Project Folder Mod321

3. Start the Docker Container
Open the Console with CTRL + J and navigate to Nils@NCRasp05:~/Mod321/Pruefung
sudo docker compose up -d --build

4. Shutdown the Docker Container if you don't need it anymore
sudo docker compose down


**Frontend-Endpoints**

**Sensor-API**
http://ncrasp05:5000/api/sensors

**MQTT-Broker**
10.5.61.199:1883
