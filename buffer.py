from colors import *

#ACTORl: (name, x = None, y = None, color = None, zone = None, threshold = None, facing = (1,0), unavailable = set(), actor_type = None, sociability = random.random(), friends = set())

corridor = {"13","14","15","16","3","6","22","28","34","41","51","58","65","70","71","72","73","79","84","89","47"}
day_room = {"50","54","57","62","64","69"}
nurse_station = {"21","31","33"}
medicine_room = {"27","32"}
patient_rooms = {"0","1","2","4","7","18","23","30","35","43","52","59","66","74","80","85","90"}
offices = {"19","20","26","37","38","39","48","49","56","63","61","76","77","78","83","87","88","44","45","46"}

#v = spawn_actors(v, tf, g, target, screen, start_in = "70", interval = range(5, 60), unavailable = offices|nurse_station|medicine_room, actor_type = "visitor")

actors = [
    {"ID":"D1", "color":blue, "actor_type":"doctor"},
    {"ID":"D2", "color":blue, "actor_type":"doctor"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":50, "y":43, "zone":"21"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":55, "y":43, "zone":"21"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":60, "y":43, "zone":"21"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":78, "y":43, "zone":"21"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":83, "y":43, "zone":"21"},
    {"ID":"N1", "color":green, "actor_type":"nurse", "x":88, "y":43, "zone":"21"},
]

spawn = {"target_zone": "20",
         "start_in": "70",
         "interval": range(5,60),
         "actor_type": "visitor",
         "unavailable": offices|nurse_station|medicine_room
        }
