from ..component import Component
from ..da import DAI
import yaml
import random
import ast

class CovidNLG(Component):
    def __init__(self, config):
        super().__init__(config)
        self.templates = self.load_templates(self.config["templates_file"])

    def load_templates(self, filename):
        
        with open(filename, 'r', encoding='utf8') as stream:
            data_loaded = yaml.safe_load(stream)
        return data_loaded
    
    def dict_to_cambridge_da(self, d):
        da_str = ''
        for i, (intent, slot_value) in enumerate(d.items()):
            if i>0:
                da_str += '|'
            da_str+=intent+'('
            for j, (slot, value) in enumerate(slot_value.items()):
                if j>0:
                    da_str += ','
                if slot != None:
                    da_str+=slot+'='+value
            da_str+=')'
        return da_str


    def __call__(self, dial, logger):
        act_dict = {}
        response = ''
        for da in dial.action:
            try:
                act_dict[da.intent].update({da.slot:da.value})
            except:
                act_dict[da.intent] = {da.slot:da.value}
        
        print(act_dict)
        for intent, slots in sorted(act_dict.items()):
            cambridge_da = self.dict_to_cambridge_da({intent:slots})
            for t, r in self.templates.items():

                try:
                    if t.format(**act_dict[intent]) == cambridge_da:
                        format_dict = act_dict[intent]
                        try:
                            data_type = slots["type"]
                        except:
                            data_type = ''
                        if data_type == 'last_year':
                            format_dict["type"] = random.choice(["Celkově za poslední rok","Celkově", "Celkem"])
                        elif data_type == 'yesterday':
                            format_dict["type"] = random.choice(["Za včerejší den", "Včera", "Ke včerejšímu dni"])
                        try:
                            locations = slots["locations"]
                            format_dict["locations"] = ''.join(['\n --> ' + l + ' (' + info["ockovaci_misto_adresa"] + ')' for l,info in ast.literal_eval(locations).items()])
                        except:
                            pass     
                        
                        response = response + ' ' + random.choice(r).format(**format_dict)

                        break
                except:
                    pass
                    
                
        print(response)
                
        
        dial.set_system_response(response)

        logger.info('Reponse: %s', str(dial.system))
        return dial
    


