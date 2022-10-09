from ..component import Component
from ..utils import choose_one
from ..da import DA, DAI
import requests
import pandas as pd
from datetime import date, timedelta
from math import radians, cos, sin, asin, sqrt
import json


def adjust_params(params, value_type):
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))
    week_ago = str(date.today() - timedelta(days=7))
    year_ago = str(date.today() - timedelta(days=365))
    
    if value_type == 'last_year':
        params.update({"datum[before]":today,
                       "datum[after]":year_ago})
    if value_type == 'yesterday':
        params.update({"datum[before]":yesterday,
                       "datum[after]":yesterday})
    if value_type == 'lastweekgrowth':
        params.update({"datum[before]":today,
                       "datum[after]":week_ago})
    if value_type == 'positiveshare':
        params.update({"datum[before]":yesterday,
                       "datum[after]":yesterday})            
    return params


def aggregate(data, value_type):
    if value_type=='last_year':
        return int(data.sum())
    elif value_type=='yesterday':
        return data[0]
    elif value_type=='lastweekgrowth':
        data = data.tolist()
        return round(((data[-1]-data[-7])/data[-7])*100,2)
    elif value_type=='positiveshare':
        return round(((data.iloc[:,1]/data.iloc[:,0])[0])*100,2)
    else:
        return data
    

def dist(row, lat2, long2):
    try:
        lat1, long1, lat2, long2 = map(radians, [float(row["latitude"]),float(row["longitude"]), float(lat2), float(long2)])
        # haversine formula 
        dlon = long2 - long1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6371* c
    except:
        km = None
    return km


def API_request(data_type, value_type):
    params = {
        'page':'1',
        'itemsPerPage':'100000',
        'apiToken':json.load(open('tokens.json'))['mzcr-api-token']
    }
    base_url = "https://onemocneni-aktualne.mzcr.cz/api/v3/"
    
    data = None
    try:
        if data_type == "ActiveCases":
            j = requests.get(url=base_url+"zakladni-prehled", params=params).json()
            data = pd.DataFrame(j['hydra:member'])['aktivni_pripady']

        if data_type in ["CovidPoints","HighCapacityCovidPoints"]:
            nominatim_url = f'https://nominatim.openstreetmap.org/search?q={value_type}&limit=1&format=json'
            j_coords = requests.get(url=nominatim_url).json()
            j = requests.get(url=base_url+"prehled-ockovacich-mist", params=params).json()
            data = pd.DataFrame(j['hydra:member'])   
            data["dist"] = data.apply(dist,lat2=pd.DataFrame(j_coords)["lat"], long2=pd.DataFrame(j_coords)["lon"],axis=1)
            if data_type == "HighCapacityCovidPoints":
                data = data[data["minimalni_kapacita"]>200]
            data = data.sort_values("dist").head(5)
            data = data[["ockovaci_misto_nazev","ockovaci_misto_adresa","minimalni_kapacita"]].set_index("ockovaci_misto_nazev").T.to_dict()

        params = adjust_params(params, value_type)
        if data_type == "Deaths":
            j = requests.get(url=base_url+"hospitalizace", params=params).json()
            data = pd.DataFrame(j['hydra:member'])['umrti']

        if data_type in ["PcrTestsPerformed","AgTestsPerformed","TotalTestsPerformed"]:
            j = requests.get(url=base_url+"testy-pcr-antigenni", params=params).json()
            data = pd.DataFrame(j['hydra:member'])
            data["PCR_pozit"] = data["PCR_pozit_sympt"]+data["PCR_pozit_asymp"]
            data["AG_pozit"] = data["AG_pozit_symp"]+data["AG_pozit_asymp_PCR_conf"]
            data["Total_testy"] = data["pocet_PCR_testy"] + data["pocet_AG_testy"] 
            data["Total_pozit"] = data["PCR_pozit"] + data["AG_pozit"]
            if data_type == "PcrTestsPerformed":
                if value_type == 'positiveshare':
                    data = data[["pocet_PCR_testy","PCR_pozit"]]
                else:
                    data = data["pocet_PCR_testy"]
            if data_type == "AgTestsPerformed":
                if value_type == 'positiveshare':
                    data = data[["pocet_AG_testy","AG_pozit"]]
                else:
                    data = data["pocet_AG_testy"]   
            if data_type == "TotalTestsPerformed":
                if value_type == 'positiveshare':
                    data = data[["Total_testy","Total_pozit"]]
                else:
                    data = data["Total_testy"]  

        if data_type in ["Vaccinations","Vaccinated"]:
            j = requests.get(url=base_url+"ockovani", params=params).json()
            data = pd.DataFrame(j['hydra:member'])   
            if data_type == "Vaccinations":
                data = data["celkem_davek"]
            else:
                data = data["druhych_davek"]

        if data_type == "Infected":
            params.update({"reportovano_khs": "true"})
            j = requests.get(url=base_url+"osoby", params=params).json()
            data = pd.DataFrame(j['hydra:member']).groupby(["datum"])["id"].count()  

        if data_type == "ForeignInfected":
            params.update({"nakaza_v_zahranici": "true",
                          "reportovano_khs": "true"})
            j = requests.get(url=base_url+"osoby", params=params).json()
            data = pd.DataFrame(j['hydra:member']).groupby(["datum"])["id"].count()  

        return_value = aggregate(data, value_type)
    except:
        return_value = 0
    return return_value


def get_action_from_request(dial,intent,slot):
    data_type = intent.replace("Request","")
    new_intent = intent.replace("Request","Provide")
    if slot == 'type':
        max_value = max(dial.state[intent][slot], key=dial.state[intent][slot].get)
        if max_value == 'None':
            dial.action.append(DAI(intent='AskType',slot=None,value=None))
        else:
            dial.action.append(DAI(intent=new_intent, slot='type',value=max_value))
            return_value = API_request(data_type, value_type=max_value)
            dial.action.append(DAI(intent=new_intent,slot='return_value',value=str(return_value)))

    if slot == 'address':
        max_value = max(dial.state[intent][slot], key=dial.state[intent][slot].get)
        if max_value == 'None':
            dial.action.append(DAI(intent='AskAddress',slot=None,value=None))
        else:
            dial.action.append(DAI(intent=new_intent, slot='address',value=max_value))
            return_value = API_request(data_type, value_type=max_value)
            dial.action.append(DAI(intent=new_intent,slot='locations',value=str(return_value)))
    return dial

class CovidPolicy(Component):
        
    def __call__(self, dial, logger):
        intents = [a.intent for a in dial.nlu]
        slots = [a.slot for a in dial.nlu]
        values = [a.value for a in dial.nlu]
        for intent, slot, value in set(zip(intents, slots, values)):
            if intent == "Greet":
                dial.action.append(DAI(intent='Greet',slot=None,value=None))

            elif intent == "Goodbye":
                dial.action.append(DAI(intent='Goodbye',slot=None,value=None))

            elif intent in ["RequestActiveCases","RequestDeaths","RequestPcrTestsPerformed","RequestAgTestsPerformed","RequestTotalTestsPerformed","RequestVaccinations",
                            "RequestVaccinated","RequestForeignInfected","RequestInfected","RequestHighCapacityCovidPoints","RequestCovidPoints","SpecifyingRequest"]:
                dial = get_action_from_request(dial, intent, slot)
            
        if len(intents) == 0:
            dial.action.append(DAI(intent='AskIntent',slot=None,value=None))
                
        return dial


        

    