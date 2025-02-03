#Inspiration : https://github.com/pimoroni/presto/blob/main/examples/word_clock.py
# World clock FR on 12h
# Touch to swith beetween 2 mode of present time after 30min 
import time

import machine
import ntptime
import pngdec
from presto import Presto


# Setup for the Presto display
presto = Presto()
display = presto.display
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(200, 200, 200)
GRAY = display.create_pen(30, 30, 30)

# Touch
touch = presto.touch


# Clear the screen before the network call is made
display.set_pen(BLACK)
display.clear()
presto.update()

# Length of time between updates in minutes.
UPDATE_INTERVAL = 1

# Offset in hours from UTC, ie -5 for NY (UTC - 5), 1 for Paris
UTC_OFFSET = 1

# Show all minutes or use "moins" X, mois quard if minutes > 30 
full_minutes="Yes"

rtc = machine.RTC()
time_string = None

matrix_fr = [
"ILBESTJMINUIT P",
"UNESEPTROISIX M",
"CINQUATREDEUX",
"HUITNEUFXONZE",
"DIXMIDIHEURES",
"ETMOINSTRENTE",
"ZLEVINGTQUART",
"QUARANTEDEMIE",
"CINQUANTEONZE",
"DIXSEIZEDOUZE",
"QUATORZETROIS",
"QUATREIZEDEUX",
"ETFUNEMGSEPTK",
"THUITQNEUFSIX"]


# WiFi setup
wifi = presto.connect()


def sync_ntp(max_retries=5, wait_time=2):
    for attempt in range(max_retries):
        try:
            ntptime.settime()  # Synchronise l'heure avec NTP
            print("Heure synchronisée avec succès !")
            return True  # Succès
        except Exception as e:
            print(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
            time.sleep(wait_time)  # Attendre avant de réessayer

    print("Impossible de joindre le serveur NTP après plusieurs essais.")
    return False  # Échec

# Exécution de la synchronisation NTP
if sync_ntp():
    print("L'heure système est maintenant synchronisée.")
else:
    print("Utilisation de l'heure locale en secours.")


# adjust utc time by offset hours
def adjust_to_timezone(rtc_datetime, offset_hours):

    # extract the time components from our tuple
    year, month, day, _, hours, minutes, seconds, _ = rtc_datetime

    # convert the current datetime tuple to a timestamp
    utc_timestamp = time.mktime((year, month, day, hours, minutes, seconds, 0, 0))

    # apply the timezone offset in seconds
    adjusted_timestamp = utc_timestamp + (offset_hours * 3600)

    # convert the adjusted timestamp back to a local datetime tuple
    adjusted_time = time.localtime(adjusted_timestamp)

    # extract adjusted values
    hours, minutes = (adjusted_time[3], adjusted_time[4])
    
    return hours, minutes



  
def approx_time_fr(hours, minutes,ampm):

    demie = [(7,8),(7,9),(7,10),(7,11),(7,12)]
    et1=[(5,0),(5,1)]
    et2=[(12,0),(12,1)]
    moins=[(5,2),(5,3),(5,4),(5,5),(5,6)]
    quart=[(6,8),(6,9),(6,10),(6,11),(6,12)]
    le=[(6,1),(6,2)]
    heures = [(4,7),(4,8),(4,9),(4,10),(4,11),(4,12)]
    coords = [(0, 0), (0, 1), (0, 3), (0, 4),(0,5)]  # "IL EST"
    coords_minus= [(0, 0), (0, 1), (0, 3), (0, 4),(0,5)] #coods_minus used to said H - x minute (so hour is hour+1)
    if ampm == "pm" :
        coords+= [(0,14),(1,14)]
        coords_minus+= [(0,14),(1,14)]
        
    heures_map = {
        0: [(0, 7), (0, 8), (0, 9), (0, 10),(0,11),(0,12)],  # "MINUIT"
        1: [(1, 0), (1, 1), (1, 2)],          # "UNE"
        2: [(2, 9), (2,10), (2, 11), (2, 12)],  # "DEUX"
        3: [(1,6),(1,7),(1,8),(1,9),(1,10)], # "TROIS
        4: [(2,3),(2,4),(2,5),(2,6),(2,7),(2,8)],
        5: [(2,0),(2,1),(2,2),(2,3)],
        6: [(1,10),(1,11),(1,12)],
        7: [(1,3),(1,4),(1,5),(1,6)],
        8: [(3,0),(3,1),(3,2),(3,3)],
        9: [(3,4),(3,5),(3,6),(3,7)],
        10:[(4,0),(4,1),(4,2)],
        11:[(3,9),(3,10),(3,11),(3,12)],
        12: [(4, 3), (4, 4), (4, 5), (4, 6)]# "MIDI"
        # Ajouter les autres heures...
    }
    

    minutes_base_maps={
        1: [(12,3),(12,4),(12,5)],
        2: [(11,9),(11,10),(11,11),(11,12)],
        3: [(10,8),(10,9),(10,10),(10,11),(10,12)],
        4: [(11,0),(11,1),(11,2),(11,3),(11,4),(11,5)],
        5: [(8,0),(8,1),(8,2),(8,3)],
        6: [(13,10),(13,11),(13,12)],
        7: [(12,8),(12,9),(12,10),(12,11)],
        8: [(13,1),(13,2),(13,3),(13,4)],
        9: [(13,6),(13,7),(13,8),(13,9)],
        10:[(9,0),(9,1),(9,2)],
        11:[(8,9),(8,10),(8,11),(8,12)],
        12:[(9,8),(9,9),(9,10),(9,11),(9,12)],
        13:[(11,3),(11,4),(11,5),(11,6),(11,7),(11,8)],
        14:[(10,0),(10,1),(10,2),(10,3),(10,4),(10,5),(10,6),(10,7)],
        15:[(5,0),(5,1),(6,8),(6,9),(6,10),(6,11),(6,12)],  #" ET QUART"
        16:[(9,3),(9,4),(9,5),(9,6),(9,7)],
        17:[(9,0),(9,1),(9,2),(12,8),(12,9),(12,10),(12,11)], # DIX SEPT
        18:[(9,0),(9,1),(9,2),(13,1),(13,2),(13,3),(13,4)], # DIX HUIT
        19:[(9,0),(9,1),(9,2),(13,6),(13,7),(13,8),(13,9)], # DIX NEUF
        20:[(6,3),(6,4),(6,5),(6,6),(6,7)],
        30:[(5,7),(5,8),(5,9),(5,10),(5,11),(5,12)],
        40:[(7,0),(7,1),(7,2),(7,3),(7,4),(7,5),(7,6),(7,7)],
        50:[(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),]
        
        }
    minutes_composed={
        21:minutes_base_maps[20]+et1+minutes_base_maps[1],
        22:minutes_base_maps[20]+minutes_base_maps[2],
        23:minutes_base_maps[20]+minutes_base_maps[3],
        24:minutes_base_maps[20]+minutes_base_maps[4],
        25:minutes_base_maps[20]+minutes_base_maps[5],
        26:minutes_base_maps[20]+minutes_base_maps[6],
        27:minutes_base_maps[20]+minutes_base_maps[7],
        28:minutes_base_maps[20]+minutes_base_maps[8],
        29:minutes_base_maps[20]+minutes_base_maps[9],
        31:minutes_base_maps[30]+et2+minutes_base_maps[1],
        32:minutes_base_maps[30]+minutes_base_maps[2],
        33:minutes_base_maps[30]+minutes_base_maps[3],
        34:minutes_base_maps[30]+minutes_base_maps[4],
        35:minutes_base_maps[30]+minutes_base_maps[5],
        36:minutes_base_maps[30]+minutes_base_maps[6],
        37:minutes_base_maps[30]+minutes_base_maps[7],
        38:minutes_base_maps[30]+minutes_base_maps[8],
        39:minutes_base_maps[30]+minutes_base_maps[9],
        41:minutes_base_maps[40]+et2+minutes_base_maps[1],
        42:minutes_base_maps[40]+minutes_base_maps[2],
        43:minutes_base_maps[40]+minutes_base_maps[3],
        44:minutes_base_maps[40]+minutes_base_maps[4],
        45:minutes_base_maps[40]+minutes_base_maps[5],
        46:minutes_base_maps[40]+minutes_base_maps[6],
        47:minutes_base_maps[40]+minutes_base_maps[7],
        48:minutes_base_maps[40]+minutes_base_maps[6],
        49:minutes_base_maps[40]+minutes_base_maps[9],
        51:minutes_base_maps[50]+et2+minutes_base_maps[1],
        52:minutes_base_maps[50]+minutes_base_maps[2],
        53:minutes_base_maps[50]+minutes_base_maps[3],
        54:minutes_base_maps[50]+minutes_base_maps[4],
        55:minutes_base_maps[50]+minutes_base_maps[5],
        56:minutes_base_maps[50]+minutes_base_maps[6],
        57:minutes_base_maps[50]+minutes_base_maps[7],
        58:minutes_base_maps[50]+minutes_base_maps[6],
        59:minutes_base_maps[50]+minutes_base_maps[9]
        }
    #minutes_maps={**minutes_base_maps,**minutes_composed} #Merge both minutes dico
    minutes_base_maps.update(minutes_composed)
    minutes_maps=minutes_base_maps.copy()
    
 
    # Define hours + 1 to manage "minus X'
    new_hours=hours
    if new_hours == 12:
        new_hours=1
    else :
        new_hours+=1
    if new_hours in heures_map:
        coords_minus += heures_map[new_hours]

    
    if hours in heures_map:
        coords += heures_map[hours]

        
    if new_hours != 0 and new_hours != 12 :
        if new_hours == 1 :
            coords_minus += heures[:-1]
        else :
            coords_minus += heures 
    if hours != 0 and hours != 12 :
        if hours == 1 :
            coords += heures[:-1]
        else :
            coords += heures
   
    if minutes > 30 and full_minutes == "No":
        if minutes == 50 :
            coords_minus+=moins+minutes_maps[10]
        elif minutes == 40 :
            coords_minus+=moins+minutes_maps[20]
        elif minutes == 55 : # "moins cinq"
            coords_minus+=moins+minutes_maps[5]
        else :
            minutes = 60 - minutes  # Transformation en "moins X"
            coords_minus+=moins+minutes_maps[minutes]        
    else:
        if minutes == 30 :  # "et demie"
            coords+=et1+demie
        elif minutes == 15:  # "et quart"
            coords+=et1+quart 
        elif minutes == 55 : # "moins cinq"
             coords_minus+=moins+minutes_maps[5]
        elif minutes in minutes_maps:
            coords += minutes_maps[minutes]
        

   
    if full_minutes == "No" or minutes == 55  :
        return coords_minus
    else:
        return coords



def update_coord():
    global time_string
    # grab the current time from the ntp server and update the Pico RTC
 #   try:
 #       ntptime.settime()
 #   except OSError:
 #       print("Unable to contact NTP server")

    current_t = rtc.datetime()
    #time_string = approx_time(current_t[4] - 12 if current_t[4] > 12 else current_t[4], current_t[5])
    
    # perform timezone adjustment here (relative to UTC)
    adjusted_hr, adjusted_min = adjust_to_timezone(current_t, UTC_OFFSET)
    time_string = approx_time_fr(adjusted_hr - 12 if adjusted_hr > 12 else adjusted_hr, adjusted_min, "pm" if adjusted_hr > 12 else "am" )

    return(time_string)

def draw_coord(active_coords):
    global time_string
    
    display.set_font("bitmap8")
    
    display.set_layer(1)

    # Clear the screen
    display.set_pen(BLACK)
    display.clear()

    default_x = 25
    x = default_x
    y = 15

    line_space = 15
    letter_space = 15
    margin = 25
    scale = 1
    spacing = 1

    for a, row in enumerate(matrix_fr):
        for b, char in enumerate(row):
            if (a, b) in active_coords:
                display.set_pen(WHITE)  # Texte blanc allumé
            else:
                display.set_pen(GRAY)     # Texte gris éteint
            display.text(char.upper(), x, y, WIDTH, scale=scale, spacing=spacing)
            x += letter_space
        y += line_space
        x = default_x
    
    presto.update()



# Set the background in layer 0
# This means we don't need to decode the image every frame

display.set_layer(0)

try:
    p = pngdec.PNG(display)

    p.open_file("wordclock_background.png")
    p.decode(0, 0)
except OSError:
    display.set_pen(BLACK)
    display.clear()





last_time = time.ticks_ms() #Use to initiat timer (limitation of sleep instruction 

def showTime() :
    active_coords=update_coord()
    draw_coord(active_coords)
    
def Test() :
    active_coords=approx_time_fr(12,50,"pm")
    draw_coord(active_coords)


showTime()
while True:
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_time) >= 30000:  # 30 secondes
        showTime()
        #Test()
        last_time = current_time  # Met à jour le dernier temps d'exécution
    touch.poll()
    if touch.state:
        if 0 <= touch.x <= 50 and 0 <= touch.y <= 50 : #Zone haut gauche
            full_minutes = "No" if full_minutes == "Yes" else "Yes"
                  
        showTime() #refesh scren after action 
        time.sleep(0.1) #micro pause 
    #time.sleep(30 * UPDATE_INTERVAL)
