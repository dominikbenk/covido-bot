from ..component import Component


class ProbabilisticDST(Component):
    """A basic state tracker that simply copies NLU results into the current dialogue
    state, overwriting any previous values."""

    def __call__(self, dial, logger):
            
        new_slot_probs = {}
        for dai in dial.nlu:
            if (dai.intent == "SpecifyingRequest") and (list(dial.state)[-1][0:7] == "Request"):
                dai.intent = list(dial.state)[-1]
                
            if dai.intent not in dial.state.keys():
                dial.state[dai.intent] = {dai.slot:{'None': 1.0}}
            
            if dai.slot not in dial.state[dai.intent].keys():
                dial.state[dai.intent][dai.slot] = {'None': 1.0}
            
            if dai.intent not in new_slot_probs.keys():    
                new_slot_probs[dai.intent] = {}   
                
            if dai.slot not in new_slot_probs[dai.intent].keys():    
                new_slot_probs[dai.intent][dai.slot] = {}    
                
            new_slot_probs[dai.intent][dai.slot].update({dai.value:dai.confidence})                  
            if dai.value not in dial.state[dai.intent][dai.slot].keys():
                dial.state[dai.intent][dai.slot].update({dai.value:0})

        
        for intent in list(dial.state.keys()):     
            for slot in list(dial.state[intent].keys()):
                for value in list(dial.state[intent][slot].keys()):
                    try:
                        coef = 1 - min([1,sum(new_slot_probs[intent][slot].values())])
                    except:
                        coef = 1
                    try:
                        dial.state[intent][slot][value] = new_slot_probs[intent][slot][value] + dial.state[intent][slot][value] * coef
                    except:
                        dial.state[intent][slot][value] = dial.state[intent][slot][value] * coef
                        
                        

                
        logger.info('State: %s', str(dial.state))
        print(dial.state)
        return dial
