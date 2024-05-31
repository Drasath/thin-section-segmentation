class State(object):

    def on_event(self, event):
        pass

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.__class__.__name__
    
class StateMachine(object):

    def __init__(self, initial_state):
        self.current_state = initial_state
        self.state_history = []

    def on_event(self, event):
        self.current_state = self.current_state.on_event(event)

    def update_history(self):
        self.state_history.append(self.current_state)
    
    def load_state(self, state):
        self.current_state = state
        # Signal that a new state has been loaded

class defaultState(State):
    def on_event(self, event):
        if event == "undo":
            print("Undo")
            return defaultState()
        elif event == "reset":
            print("Reset")
            return defaultState()
        elif event == "segment":
            print("Segment")
            return defaultState()
        elif event == "selectRegion":
            print("Select Region")
            return defaultState()
        elif event == "printAMG":
            print("Print AMG")
            return defaultState()
        else:
            return self