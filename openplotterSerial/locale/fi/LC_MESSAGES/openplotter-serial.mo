��    _                       	     *     E     J     Y     e     t     �  2   �     �     �     �     	     	  Y   	  $   u	     �	     �	     �	  H   �	     �	     
     
     
     8
  -   A
  -   o
  +   �
     �
     �
  %     -   '     U     Z     ]     b     i  (   |  (   �  3   �             �   ;  s   �  G   =  `   �  U   �  1   <  I   n  5   �  .   �          &  ,   .  &   [     �     �     �     �  $   �     �               &     /  K   I     �  4   �  \   �  \   A  C   �  }   �     `     e  r   n  ^   �     @     F  
   L     W     g     l     s  
   |     �     �     �     �     �     �     �  
   �     �     �  *  �          4     S     X     k     {     �  "   �  1   �     �     
          )     7  \   C  $   �     �     �     �  M   �     ,     ?     H  "   P     s  .   �  4   �  2   �  &     &   B  ,   i  5   �     �     �     �     �     �      �  $     -   ?     m     �  �   �  w   /  Q   �  t   �  L   n  6   �  Q   �  E   D  +   �     �  	   �  /   �  $   �       "   $     G  &   \  ,   �     �     �     �  	   �     �  R        U  .   l  p   �  s      L   �   �   �      `!  
   e!  s   p!  g   �!     L"     R"     Y"     `"     o"     v"     |"     �"     �"     �"     �"     �"     �"     �"     �"     �"     �"  
   #     	      $   (                        0          -   1   O   C       F      D      4   R              "   :   6         ?      V   ^   G       8   P   U       K   S       )   L   9   '   W       @                    >   
       ]   +   5           T       X      I   [   A       \          E           %          ;                     J   2   B   .   #   H          7       3      Q      M   _   N   !   Z          <   =   *              Y                     ,         /   &     is connected to a reserved port (or motor controller data) AUTO Add to CAN Bus Add to GPSD Add to Pypilot Add to Signal K Adding connection for device:  All your serial connections have an assigned alias Applied changes Apply Applying changes ... Are you sure? Baud Rate:  Be sure you send only GNSS or AIS data to GPSD. Baud Rate will be automatically assigned. Checking serial connections alias... Connections DONE Data:  Device with duplicate vendor and product must be set to "Remember port". Device with vendor  Devices Edit Editing GPSD config file... FAILED:  Failed. Error creating connection in Signal K Failed. Error removing connection in Signal K Failed. Error setting the device in Pypilot Failed. No port selected Failed. This ID already exists Failed. This device is already in use Failed. This device is already set in Pypilot Help ID ID:  MANUAL No device selected Please install "CAN Bus" OpenPlotter app Please install "Pypilot" OpenPlotter app Please install "Signal K Installer" OpenPlotter app Please install "gpsd" package Please select type of data Press AUTO to add this device to the list of devices managed by GPSD. A connection for GPSD will be created in Signal K if it does not exist. Press AUTO to create a "canboatjs" connection for a NGT-1 or a CAN-USB device in Signal K using the settings above. Press AUTO to create a connection in Signal K using the settings above. Press AUTO to use this device to send data to Pypilot. Baud Rate will be automatically assigned. Press MANUAL if you need to add special settings or you want to set a CANable device. Press MANUAL if you need to add special settings. Press MANUAL if you prefer to set this device in openplotter-pypilot app. Pypilot serial devices modified and autopilot enabled Pypilot will get data from GPSD automatically. Question Refresh Remember device (by vendor, product, serial) Remember port (positon on the USB-hub) Remove Removing GPSD config file... Removing version... Restarting Signal K server...  Same alias used for multiple devices Serial Serial port:  Setting version... Settings Signal K server restarted The alias must be a lowercase string between 1 and 8 characters or numbers. There are missing devices There are serial connections with no alias assigned: This action disables Bluetooth and enables UART interface in GPIO. OpenPlotter will reboot.
 This action disables UART interface in GPIO and enables Bluetooth. OpenPlotter will reboot.
 This port is already reserved and must be set to "Remember device". To get data in OpenCPN, make sure this network connection exists in OpenCPN:
Protocol: Signal K
Address: localhost
DataPort:  UART USB port Use "SK → NMEA 2000" plugin to send data from Signal K to your CAN network. Open desired TX PGNs in your device. You can also set the motor controller in this way, but make sure you have enabled UART before. alias bauds connection connection ID:  data device device:  lower left lower right middle left middle right no Hub product remember serial upper left upper right vendor Project-Id-Version: openplotter
POT-Creation-Date: 2020-09-24 18:29+0200
PO-Revision-Date: 2020-09-26 13:36+0200
Last-Translator: 
Language-Team: Finnish
Language: fi
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 1.8.7.1
X-Poedit-Basepath: ../../..
Plural-Forms: nplurals=2; plural=(n != 1);
X-Poedit-SourceCharset: UTF-8
X-Crowdin-Project: openplotter
X-Crowdin-Project-ID: 289888
X-Crowdin-Language: fi
X-Crowdin-File: openplotter-serial.po
X-Crowdin-File-ID: 17
X-Poedit-SearchPath-0: .
  on kytketty varattuun porttiin (tai moottorin hallinnan data) AUTO Lisää CAN Busiin Lisää GPSDhen Lisää Pypilotiin Lisää Signal Khon Lisätään kytkentä laitteelle:  Kaikilla sarjaliitännöillä on nimi liitettynä Lisätyt muutokset Käytä Toteutaan muutoksia... Oletko varma? Baud Arvo:  Varmista, että lähetät vain GNSS tai AIS dataa GPSDhen. Baudit asetetaan automaattisesti. Tutkitaan sarjaliitännän nimeä... Yhteydet VALMIS Tiedot:  Kahden toimittajan tuotteet on määritettävä ”muista portit” kohdassa. Toimittajan laite  Laitteet Muokkaa Muokataan GPSD asetus tiedostoa... EPÄONNISTUNUT:  Epäonnistui. Virhe kytkettäessä Signal Khon Epäonnistui. Virhe kytkennän poistossa Signal Kssa Epäonnistui. Virhe laitteen Pypilotin asetuksissa Epäonnistui. Porttia ei ollut valittu Epäonnistui. Tämä ID on jo olemassa Epäonnistui. Tämä laite on jo käytössä Epäonnistui. Tämä laite on jo asetettu Pypilotissa Ohje ID ID:  KÄSIN Ei ole valittua laitetta Asenna "CAN Bus" OpenPlotter app Asenna "Pypilot" OpenPlotter sovelma Asenna "Signal K asennin" OpenPlotter sovelma Asenna "gpsd" paketti Valitse datan tyyppi Paina AUTO lisätäksesi tämän laitteen GPSD:n hallinnoimien laitteiden luetteloon. GPSD:lle luodaan yhteys Signal K:ssa, jos sitä ei ole olemassa. Paina AUTO, jos haluat tehdä "canboatjs" yhteyden NGT-1 tai CAN-USB laitteelle Signal Kssa yllä olevilla asetuksilla. Paina AUTO, jos haluat muodostaa yhteyden Signal Khon yllä olevilla asetuksilla. Paina AUTO käyttääksesi tätä laitetta lähettämään dataa Pypilotille. Bauditaso määrittyy automaattisesti. Paina MANUAL, jos tarvitset erikoiasetuksia tai haluat asettaa CAN laitteen. Paina MANUAL jos on tarpeen lisätä erikoisasetuksia. Paina MANUAL, jos käytät tätä laitetta mieluimmin openplotter-pypilot apilla. Pypilotin sarjalaitteisto on muokattu ja automaattiohjain käytössä Pypilot saa dataa GPSDstä automaattisesti. Kysymys Virkistä Muistaa laitteen (myyjä, tuote-, sarja-numero) Muistaa portin (paikkan USB-hubissa) Poista Poistetaan GPSD asetus tiedosto... Poistetaan versio... Käynnistetään Signal K palvelin...  Samaa nimeä käytetään useilla laitteilla Sarja Sarjaportti:  Asetetaan versio... Asetukset Signal K palvelin käynnistetty Aliaksen pitää olla 1stä 8aan merkkiä pitkä, pieniä kirjaimia tai numeroita. On puuttuvia laitteita On sarjaliitäntöjä ilman liitettyä nimeä: Tämä toiminto estää Bluetoothin ja mahdollistaa UART rajapinnan GPIO:on. OpenPlotter käynnistyy uudelleen.
 Tämä toiminto poistaa käytöstä UARTin GPIOssa ja mahdollistaa Bluetoothin. OpenPlotter käynnistyy uudelleen.
 Tämä portti on jo varattu ja määritettävä ”muista laite” kohdassa. Saadaksesi tietoja OpenCPN: stä, varmista, että tämä verkkoyhteys on olemassa OpenCPN: ssä:
Protokolla: Signal K
Osoite: localhost
DataPort:  UART USB portti Käytä "SK -> NMEA 2000" pluginia datan siirtämiseksi Signal Ksta CAN verkkoon. Avaa oikeat TX PGNt laitteessasi. Voit myös asettaa moottorin ohjaimen tällä tavalla, mutta varmista ensin, että UART on käytössä. alias baudit yhteys kytkentä ID:  tiedot laite laite:  alas vasemmalle alas oikealle keskellä vasemmalla keskellä oikealla ei Hubia tuote muista sarja ylös vasemmalle ylös oikealle toimittaja 