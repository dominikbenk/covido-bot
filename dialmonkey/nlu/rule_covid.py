from ..component import Component
from ..da import DAI
import re


class CovidNLU(Component):

    def __call__(self, dial, logger):
        
        if re.findall('ahoj|zdravim|dobry den|cau|cus|zdar', dial.user):
            dial.nlu.append(DAI(intent='Greet',slot=None,value=None, confidence=1))
            
        if re.findall('aktivni', dial.user):
            if re.findall('vcer', dial.user):
                value = 'yesterday'
            else:
                value = 'None'
            dial.nlu.append(DAI(intent='RequestActiveCases',slot='type',value=value, confidence=1))
            
            
        if re.findall('umrt|smrt|umrel|podlehl|zahynul', dial.user):
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            else:
                value = 'None'
            dial.nlu.append(DAI(intent='RequestDeaths',slot='type',value=value, confidence=1))
            
        if re.findall('test', dial.user):
            if re.findall(' pcr ', dial.user):
                intent = 'RequestPcrTestsPerformed'
            elif re.findall(' ag |antigen', dial.user):
                intent = 'RequestAgTestsPerformed'
            else:
                intent = 'RequestTotalTestsPerformed'            
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            elif re.findall('pozitivn|podil', dial.user):
                value = 'positiveshare'  
            else:
                value = 'None'
            dial.nlu.append(DAI(intent=intent,slot='type',value=value, confidence=1)) 
            
        if re.findall('vakcin|ockovani', dial.user):
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            else:
                value = 'None'
            dial.nlu.append(DAI(intent='RequestVaccinations',slot='type',value=value, confidence=1))          
            
        if re.findall('vakcinovany|ockovany', dial.user):
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            else:
                value = 'None'
            dial.nlu.append(DAI(intent='RequestVaccinated',slot='type',value=value, confidence=1)) 

        if re.findall('infik|onemoc|nakaz|nakaz|infekc', dial.user):
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            else:
                value = 'None'
            if re.findall('stat|zahranic|zeme|zemi', dial.user):
                intent = 'RequestForeignInfected'
            else:
                intent = 'RequestInfected'
            dial.nlu.append(DAI(intent=intent,slot='type',value=value, confidence=1)) 
            
        if re.findall('odberov|mista', dial.user):
            if re.findall('kapacit', dial.user):
                intent = 'RequestHighCapacityCovidPoints'
            else:
                intent = 'RequestCovidPoints'
            try:
                value = re.search(' (ulice|adrese) .*[0-9]',dial.user).group(0).strip().replace('ulice ','').replace('adrese ','')
            except:
                value = 'None'
            dial.nlu.append(DAI(intent=intent,slot='address',value=value, confidence=1))             
        
        if re.findall('nashle|dekuj|diky', dial.user):
            da_item = DAI(intent='Goodbye',slot=None,value=None, confidence=1)
            dial.nlu.append(da_item)
            
        if len(dial.nlu) == 0:
            if re.findall('rok|rocn|celkov', dial.user):
                value = 'last_year'
            elif re.findall('vcer', dial.user):
                value = 'yesterday'
            elif re.findall('narust|narostl', dial.user):
                value = 'lastweekgrowth'
            try:
                da_item = DAI(intent='SpecifyingRequest',slot='type',value=value, confidence=1)
                dial.nlu.append(da_item)
            except:
                pass
            
            
        print(str(dial.nlu))
        logger.info('NLU: %s', str(dial.nlu))
        return dial
